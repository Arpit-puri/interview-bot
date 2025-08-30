import { useEffect, useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface SessionStatus {
  question_count: number;
  current_phase: string;
  total_questions: number;
  interview_completed: boolean;
  manually_ended: boolean;
  progress_percentage: number;
}

interface ChatProps {
  sessionId: string;
  roleTitle: string;
  onTimerUpdate: (seconds: number) => void;
  onInterviewEnd: (finalTime: number) => void;
}

export default function Chat({ sessionId, roleTitle, onTimerUpdate, onInterviewEnd }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewEnded, setInterviewEnded] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null);

  // Fetch session status
  const fetchSessionStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/status`);
      const status = await response.json();
      setSessionStatus(status);
      
      if (status.interview_completed && !interviewEnded) {
        setInterviewEnded(true);
        onInterviewEnd(elapsedSeconds);
      }
    } catch (error) {
      console.error("Error fetching session status:", error);
    }
  };

  useEffect(() => {
    fetch(`http://localhost:8000/api/sessions/${sessionId}/history`)
      .then((res) => res.json())
      .then((data) => {
        setMessages(data);
        setInterviewStarted(data.length > 0);
        // If interview was already started, set start time to now for timer
        if (data.length > 0) {
          setStartTime(new Date());
        }
      });
    
    // Fetch initial session status
    fetchSessionStatus();
  }, [sessionId]);

  // Timer effect
  useEffect(() => {
    let interval: number | null = null;
    
    if (startTime && interviewStarted && !interviewEnded) {
      interval = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now.getTime() - startTime.getTime()) / 1000);
        setElapsedSeconds(elapsed);
        onTimerUpdate(elapsed);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [startTime, interviewStarted, interviewEnded, onTimerUpdate]);

  const endInterview = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/sessions/end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      
      const data = await response.json();
      
      if (data.response) {
        setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      }
      
      setInterviewEnded(true);
      onInterviewEnd(elapsedSeconds);
      fetchSessionStatus();
    } catch (error) {
      console.error("Error ending interview:", error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || interviewEnded) return;
    
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setInterviewStarted(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      });

      const data = await res.json();
      
      if (data.error) {
        console.error("Chat error:", data.error);
        return;
      }
      
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      
      // Check if interview completed automatically
      if (data.interview_completed) {
        setInterviewEnded(true);
        onInterviewEnd(elapsedSeconds);
      }
      
      // Fetch updated session status
      fetchSessionStatus();
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };
  const sendMessageStream = async () => {
    if (!input.trim() || interviewEnded) return;
  
    // Add user message immediately
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setInterviewStarted(true);
  
    try {
      const res = await fetch("http://localhost:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, session_id: sessionId }),
      });
  
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
  
      let assistantMsg = ""; // Accumulate tokens here
  
      while (true) {
        const { value, done } = await reader!.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        assistantMsg += chunk;
  
        // Update UI progressively
        setMessages((prev) => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg && lastMsg.role === "assistant") {
            // Update the last assistant message
            return [...prev.slice(0, -1), { role: "assistant", content: assistantMsg }];
          } else {
            // First chunk — add new assistant message
            return [...prev, { role: "assistant", content: assistantMsg }];
          }
        });
      }
  
      // Fetch updated session status after streaming
      fetchSessionStatus();
  
    } catch (error) {
      console.error("Error streaming message:", error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const startInterview = async () => {
    setIsLoading(true);
    setInterviewStarted(true);
    const now = new Date();
    setStartTime(now);

    try {
      const res = await fetch("http://localhost:8000/api/sessions/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      const data = await res.json();
      setMessages([{ role: "assistant", content: data.response }]);
      fetchSessionStatus();
    } catch (error) {
      console.error("Error starting interview:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getPhaseColor = (phase: string) => {
    const colors: Record<string, string> = {
      greeting: "#10b981", // green
      easy: "#06b6d4", // cyan  
      moderate: "#3b82f6", // blue
      scenario: "#8b5cf6", // violet
      hard: "#f59e0b", // amber
      expert: "#ef4444", // red
      completed: "#10b981" // green
    };
    return colors[phase] || "#6b7280";
  };

  const getPhaseEmoji = (phase: string) => {
    const emojis: Record<string, string> = {
      greeting: "👋",
      easy: "🟢",
      moderate: "🔵", 
      scenario: "🎯",
      hard: "🟠",
      expert: "🔴",
      completed: "✅"
    };
    return emojis[phase] || "❓";
  };

  return (
    <div
      style={{
        width: "100%",
        maxWidth: 800,
        display: "flex",
        flexDirection: "column",
        gap: 24,
      }}
    >
      {/* Progress Bar - Show when interview started */}
      {interviewStarted && sessionStatus && (
        <div
          style={{
            background: "rgba(255,255,255,0.1)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            borderRadius: 20,
            border: "1px solid rgba(255,255,255,0.2)",
            padding: 20,
            boxShadow: "0 8px 32px rgba(0,0,0,0.1)"
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 12
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 18 }}>{getPhaseEmoji(sessionStatus.current_phase)}</span>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: getPhaseColor(sessionStatus.current_phase),
                  textTransform: "capitalize"
                }}
              >
                {sessionStatus.current_phase === "completed" ? "Interview Complete" : `${sessionStatus.current_phase} Phase`}
              </span>
            </div>
            <span
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: "rgba(0,0,0,0.7)",
                fontFamily: "monospace"
              }}
            >
              {sessionStatus.question_count}/{sessionStatus.total_questions}
            </span>
          </div>
          
          {/* Progress Bar */}
          <div
            style={{
              width: "100%",
              height: 8,
              background: "rgba(0,0,0,0.1)",
              borderRadius: 4,
              overflow: "hidden"
            }}
          >
            <div
              style={{
                width: `${sessionStatus.progress_percentage}%`,
                height: "100%",
                background: `linear-gradient(90deg, ${getPhaseColor(sessionStatus.current_phase)}, ${getPhaseColor(sessionStatus.current_phase)}dd)`,
                transition: "width 0.5s ease",
                borderRadius: 4
              }}
            />
          </div>
          
          {/* Phase Description */}
          <div
            style={{
              marginTop: 8,
              fontSize: 12,
              color: "rgba(0,0,0,0.6)",
              textAlign: "center"
            }}
          >
            {sessionStatus.current_phase === "greeting" && "Getting to know you"}
            {sessionStatus.current_phase === "easy" && "Warming up with fundamentals"}
            {sessionStatus.current_phase === "moderate" && "Diving into practical knowledge"}
            {sessionStatus.current_phase === "scenario" && "Real-world problem solving"}
            {sessionStatus.current_phase === "hard" && "Advanced challenges"}
            {sessionStatus.current_phase === "expert" && "Expert-level mastery"}
            {sessionStatus.current_phase === "completed" && "All questions completed!"}
          </div>
        </div>
      )}

      {/* Chat Container */}
      <div
        style={{
          background: "rgba(255,255,255,0.1)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          borderRadius: 32,
          border: "1px solid rgba(255,255,255,0.2)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.2)",
          overflow: "hidden",
        }}
      >
        {/* Messages Area */}
        <div
          style={{
            padding: 32,
            minHeight: 500,
            maxHeight: 600,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 20,
          }}
        >
          {messages.length === 0 && !interviewStarted ? (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                flexDirection: "column",
                textAlign: "center",
                color: "rgba(0,0,0,0.7)",
              }}
            >
              <div
                style={{
                  fontSize: 64,
                  marginBottom: 20,
                  animation: "pulse 2s ease-in-out infinite"
                }}
              >
                🎯
              </div>
              <h3
                style={{
                  margin: 0,
                  fontSize: 28,
                  fontWeight: 700,
                  marginBottom: 12,
                  color: "#1a1a1a",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                {roleTitle} Interview
              </h3>
              <p style={{ 
                margin: "0 0 16px 0", 
                fontSize: 16, 
                opacity: 0.8,
                lineHeight: 1.5,
                maxWidth: 400
              }}>
                Ready to showcase your expertise? This interview consists of <strong>19 questions</strong> across different difficulty levels.
              </p>
              <div
                style={{
                  background: "rgba(255,255,255,0.1)",
                  borderRadius: 12,
                  padding: 16,
                  marginBottom: 24,
                  border: "1px solid rgba(255,255,255,0.2)"
                }}
              >
                <div style={{ fontSize: 14, color: "rgba(0,0,0,0.7)" }}>
                  <div style={{ marginBottom: 8, fontWeight: 600 }}>📋 Interview Structure:</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
                    <span style={{ background: "rgba(16,185,129,0.2)", padding: "2px 8px", borderRadius: 8, fontSize: 12 }}>👋 Greeting (1)</span>
                    <span style={{ background: "rgba(6,182,212,0.2)", padding: "2px 8px", borderRadius: 8, fontSize: 12 }}>🟢 Easy (7)</span>
                    <span style={{ background: "rgba(59,130,246,0.2)", padding: "2px 8px", borderRadius: 8, fontSize: 12 }}>🔵 Moderate (4)</span>
                    <span style={{ background: "rgba(139,92,246,0.2)", padding: "2px 8px", borderRadius: 8, fontSize: 12 }}>🎯 Scenario (2)</span>
                    <span style={{ background: "rgba(245,158,11,0.2)", padding: "2px 8px", borderRadius: 8, fontSize: 12 }}>🟠 Hard (3)</span>
                    <span style={{ background: "rgba(239,68,68,0.2)", padding: "2px 8px", borderRadius: 8, fontSize: 12 }}>🔴 Expert (2)</span>
                  </div>
                </div>
              </div>
              <button
                onClick={startInterview}
                disabled={isLoading}
                style={{
                  padding: "16px 32px",
                  borderRadius: 20,
                  border: "none",
                  background: isLoading 
                    ? "rgba(255,255,255,0.3)" 
                    : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#fff",
                  fontWeight: 600,
                  fontSize: 18,
                  cursor: isLoading ? "not-allowed" : "pointer",
                  boxShadow: isLoading 
                    ? "none" 
                    : "0 12px 40px rgba(102,126,234,0.4)",
                  transition: "all 0.3s ease",
                  opacity: isLoading ? 0.6 : 1,
                }}
                onMouseEnter={e => {
                  if (isLoading) return;
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = "0 16px 48px rgba(102,126,234,0.5)";
                }}
                onMouseLeave={e => {
                  if (isLoading) return;
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 12px 40px rgba(102,126,234,0.4)";
                }}
              >
                {isLoading ? "Starting Interview..." : "🚀 Start Interview"}
              </button>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                    alignItems: "flex-start",
                    gap: 12,
                  }}
                >
                  {/* Avatar */}
                  {msg.role === "assistant" && (
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: "50%",
                        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 18,
                        flexShrink: 0,
                        boxShadow: "0 4px 20px rgba(102,126,234,0.3)"
                      }}
                    >
                      🎯
                    </div>
                  )}
                  
                  {/* Message Bubble */}
                  <div
                    style={{
                      maxWidth: "75%",
                      padding: "16px 20px",
                      borderRadius: 24,
                      background: msg.role === "user"
                        ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                        : "rgba(255,255,255,0.15)",
                      color: msg.role === "user" ? "#fff" : "#1a1a1a",
                      fontSize: 16,
                      lineHeight: 1.6,
                      boxShadow: msg.role === "user"
                        ? "0 8px 32px rgba(102,126,234,0.3)"
                        : "0 8px 32px rgba(0,0,0,0.1)",
                      border: msg.role === "assistant" ? "1px solid rgba(255,255,255,0.2)" : "none",
                      borderTopRightRadius: msg.role === "user" ? 8 : 24,
                      borderTopLeftRadius: msg.role === "user" ? 24 : 8,
                      wordBreak: "break-word",
                      whiteSpace: "pre-wrap",
                      position: "relative"
                    }}
                  >
                    {msg.content}
                  </div>
                  
                  {/* User Avatar */}
                  {msg.role === "user" && (
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: "50%",
                        background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 18,
                        flexShrink: 0,
                        boxShadow: "0 4px 20px rgba(240,147,251,0.3)"
                      }}
                    >
                      👤
                    </div>
                  )}
                </div>
              ))}
              
              {/* Interview Completion Message */}
              {interviewEnded && sessionStatus && (
                <div
                  style={{
                    background: sessionStatus.manually_ended 
                      ? "rgba(245,158,11,0.1)" 
                      : "rgba(16,185,129,0.1)",
                    border: `1px solid ${sessionStatus.manually_ended ? "rgba(245,158,11,0.3)" : "rgba(16,185,129,0.3)"}`,
                    borderRadius: 16,
                    padding: 20,
                    textAlign: "center",
                    color: sessionStatus.manually_ended ? "#d97706" : "#059669",
                    fontWeight: 600
                  }}
                >
                  <div style={{ fontSize: 24, marginBottom: 8 }}>
                    {sessionStatus.manually_ended ? "⚡" : "🎉"}
                  </div>
                  <div style={{ fontSize: 16 }}>
                    {sessionStatus.manually_ended 
                      ? "Interview ended early - Thank you for your time!"
                      : "Interview completed successfully!"
                    }
                  </div>
                  <div style={{ fontSize: 14, opacity: 0.8, marginTop: 4 }}>
                    Questions answered: {sessionStatus.question_count}/{sessionStatus.total_questions}
                  </div>
                </div>
              )}
            </>
          )}
          
          {/* Loading Indicator */}
          {isLoading && (
            <div
              style={{
                display: "flex",
                justifyContent: "flex-start",
                alignItems: "flex-start",
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: "50%",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 18,
                  flexShrink: 0,
                  boxShadow: "0 4px 20px rgba(102,126,234,0.3)"
                }}
              >
                🎯
              </div>
              <div
                style={{
                  padding: "16px 20px",
                  borderRadius: 24,
                  background: "rgba(255,255,255,0.15)",
                  border: "1px solid rgba(255,255,255,0.2)",
                  borderTopLeftRadius: 8,
                  display: "flex",
                  gap: 4,
                  alignItems: "center"
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: "rgba(26,26,26,0.6)",
                    animation: "pulse 1.5s ease-in-out 0s infinite"
                  }}
                />
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: "rgba(26,26,26,0.6)",
                    animation: "pulse 1.5s ease-in-out 0.2s infinite"
                  }}
                />
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: "rgba(26,26,26,0.6)",
                    animation: "pulse 1.5s ease-in-out 0.4s infinite"
                  }}
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Input Area - only show if interview started and not ended */}
        {interviewStarted && !interviewEnded && (
          <div
            style={{
              padding: "24px 32px",
              background: "rgba(255,255,255,0.05)",
              borderTop: "1px solid rgba(255,255,255,0.1)"
            }}
          >
            <form
              style={{ display: "flex", alignItems: "center", gap: 12 }}
              onSubmit={e => {
                e.preventDefault();
                sendMessage();
              }}
            >
              <div style={{ flex: 1, position: "relative" }}>
                <textarea
                  style={{
                    width: "100%",
                    padding: "16px 20px",
                    borderRadius: 20,
                    border: "1.5px solid #cbd5e1",
                    outline: "none",
                    fontSize: 16,
                    background: "rgba(255,255,255,0.9)",
                    color: "#000",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.06), 0 1.5px 0 #e5e7eb",
                    transition: "all 0.3s ease",
                    resize: "none",
                    minHeight: 56,
                    maxHeight: 120,
                    lineHeight: 1.5,
                    fontFamily: "inherit",
                    backdropFilter: "blur(4px)",
                    WebkitBackdropFilter: "blur(4px)"
                  }}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessageStream();
                    }
                  }}
                  onFocus={e => {
                    e.target.style.border = "1px solid rgba(102,126,234,0.5)";
                    e.target.style.boxShadow = "inset 0 2px 10px rgba(0,0,0,0.1), 0 0 0 3px rgba(102,126,234,0.1)";
                  }}
                  onBlur={e => {
                    e.target.style.border = "1px solid rgba(255,255,255,0.2)";
                    e.target.style.boxShadow = "inset 0 2px 10px rgba(0,0,0,0.1)";
                  }}
                  placeholder="Type your answer... (Shift+Enter for new line)"
                  disabled={isLoading || interviewEnded}
                />
              </div>
              <button
                type="submit"
                disabled={!input.trim() || isLoading || interviewEnded}
                style={{
                  padding: "8px 16px",
                  borderRadius: 16,
                  border: "none",
                  background: (!input.trim() || isLoading || interviewEnded) 
                    ? "rgba(255,255,255,0.1)" 
                    : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#fff",
                  fontWeight: 600,
                  fontSize: 18,
                  cursor: (!input.trim() || isLoading || interviewEnded) ? "not-allowed" : "pointer",
                  boxShadow: (!input.trim() || isLoading || interviewEnded) 
                    ? "none" 
                    : "0 8px 32px rgba(102,126,234,0.3)",
                  transition: "all 0.3s ease",
                  minWidth: 44,
                  height: 44,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  opacity: (!input.trim() || isLoading || interviewEnded) ? 0.5 : 1,
                  marginLeft: 32
                }}
                onMouseEnter={e => {
                  if (!input.trim() || isLoading || interviewEnded) return;
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = "0 12px 40px rgba(102,126,234,0.4)";
                }}
                onMouseLeave={e => {
                  if (!input.trim() || isLoading || interviewEnded) return;
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 8px 32px rgba(102,126,234,0.3)";
                }}
              >
                {isLoading ? "⏳" : "🚀"}
              </button>
            </form>
          </div>
        )}
        
        {/* End Interview Button - Show only when interview is active and not ended */}
        {interviewStarted && !interviewEnded && (
          <div
            style={{
              padding: "16px 32px",
              borderTop: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(239,68,68,0.05)",
              display: "flex",
              justifyContent: "center"
            }}
          >
            <button
              onClick={endInterview}
              style={{
                padding: "8px 20px",
                borderRadius: 16,
                border: "1px solid rgba(239,68,68,0.3)",
                background: "rgba(239,68,68,0.1)",
                color: "#dc2626",
                fontSize: 14,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.3s ease",
                display: "flex",
                alignItems: "center",
                gap: 8
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = "rgba(239,68,68,0.2)";
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = "rgba(239,68,68,0.1)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <span>🏁</span>
              End Interview Early
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
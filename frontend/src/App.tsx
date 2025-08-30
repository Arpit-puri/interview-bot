import { useEffect, useState } from "react";
import Chat from "./components/Chat";
import RoleSelection from "./components/RoleSelection";

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedRoleTitle, setSelectedRoleTitle] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [interviewEnded, setInterviewEnded] = useState(false);
  const [finalInterviewTime, setFinalInterviewTime] = useState<number | null>(null);

  useEffect(() => {
    document.body.style.background = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)";
    document.body.style.minHeight = "100vh";
    document.body.style.margin = "0";
    document.body.style.fontFamily = "'Inter', sans-serif";
  }, []);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleRoleSelect = async (roleId: string, roleTitle: string) => {
    setIsInitializing(true);
    setSelectedRole(roleId);
    setSelectedRoleTitle(roleTitle);

    try {
      const response = await fetch("http://localhost:8000/api/sessions/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role_id: roleId })
      });
      
      const data = await response.json();
      setSessionId(data.session_id);
    } catch (error) {
      console.error("Error initializing session:", error);
    } finally {
      setIsInitializing(false);
    }
  };

  const handleBackToRoles = () => {
    setSelectedRole(null);
    setSelectedRoleTitle(null);
    setSessionId(null);
    setElapsedSeconds(0);
    setInterviewEnded(false);
    setFinalInterviewTime(null);
  };

  const handleTimerUpdate = (seconds: number) => {
    setElapsedSeconds(seconds);
  };

  const handleInterviewEnd = (finalTime: number) => {
    setInterviewEnded(true);
    setFinalInterviewTime(finalTime);
  };

  if (isInitializing) {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        }}
      >
        <div
          style={{
            background: "rgba(255,255,255,0.2)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            borderRadius: 24,
            padding: 40,
            textAlign: "center",
            border: "1px solid rgba(255,255,255,0.3)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.1)"
          }}
        >
          <div
            style={{
              fontSize: 48,
              marginBottom: 20,
              animation: "pulse 1.5s ease-in-out infinite"
            }}
          >
            🚀
          </div>
          <h2
            style={{
              fontSize: 24,
              fontWeight: 600,
              color: "#333",
              margin: "0 0 12px 0"
            }}
          >
            Preparing Your Interview
          </h2>
          <p
            style={{
              fontSize: 16,
              color: "rgba(0,0,0,0.6)",
              margin: 0
            }}
          >
            Setting up questions for {selectedRoleTitle}...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: selectedRole ? "flex-start" : "center",
        minHeight: "100vh",
        width: "100vw",
        position: "relative"
      }}
    >
      {/* Header - only show when in interview */}
      {selectedRole && sessionId && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            zIndex: 100,
            background: "rgba(255,255,255,0.1)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            border: "1px solid rgba(255,255,255,0.2)",
            boxShadow: "0 8px 32px rgba(31,38,135,0.15)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "20px 40px",
              maxWidth: 1200,
              margin: "0 auto"
            }}
          >
            <button
              onClick={handleBackToRoles}
              style={{
                padding: "8px 16px",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.3)",
                background: "rgba(255,255,255,0.2)",
                color: "#333",
                fontSize: 14,
                fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.3s ease",
                backdropFilter: "blur(10px)"
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = "rgba(255,255,255,0.3)";
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = "rgba(255,255,255,0.2)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              ← Back to Roles
            </button>
            
            <h1
              style={{
                textAlign: "center",
                margin: 0,
                fontWeight: 700,
                fontSize: 28,
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              🎯 {selectedRoleTitle} Interview
            </h1>
            
            {/* Timer Display */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "8px 16px",
                borderRadius: 12,
                background: "rgba(255,255,255,0.15)",
                border: "1px solid rgba(255,255,255,0.2)",
                backdropFilter: "blur(10px)",
                boxShadow: "0 4px 16px rgba(0,0,0,0.1)"
              }}
            >
              <div
                style={{
                  fontSize: 16,
                  animation: elapsedSeconds > 0 && !interviewEnded ? "pulse 2s ease-in-out infinite" : "none"
                }}
              >
                {interviewEnded ? "✅" : "⏱️"}
              </div>
              <span
                style={{
                  fontSize: 16,
                  fontWeight: 600,
                  color: interviewEnded ? "#22c55e" : "#333",
                  fontFamily: "monospace",
                  minWidth: 60,
                  textAlign: "center"
                }}
              >
                {finalInterviewTime ? formatTime(finalInterviewTime) : formatTime(elapsedSeconds)}
              </span>
              {interviewEnded && (
                <div
                  style={{
                    padding: "4px 8px",
                    borderRadius: 8,
                    border: "1px solid rgba(34,197,94,0.3)",
                    background: "rgba(34,197,94,0.15)",
                    color: "#16a34a",
                    fontSize: 12,
                    fontWeight: 600,
                    marginLeft: 8
                  }}
                >
                  🎉 Complete
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Main Content */}
      <div style={{ 
        width: "100%",
        marginTop: selectedRole ? 100 : 0,
        display: "flex", 
        justifyContent: "center",
        padding: "0 20px"
      }}>
        {!selectedRole ? (
          <RoleSelection onRoleSelect={handleRoleSelect} />
        ) : sessionId ? (
          <Chat 
            sessionId={sessionId} 
            roleTitle={selectedRoleTitle!} 
            onTimerUpdate={handleTimerUpdate}
            onInterviewEnd={handleInterviewEnd}
          />
        ) : null}
      </div>
    </div>
  );
}

export default App;
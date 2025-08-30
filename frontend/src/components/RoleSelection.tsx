import { useState } from "react";

interface Role {
  id: string;
  title: string;
  icon: string;
  description: string;
  duration: string;
  difficulty: string;
}

const roles: Role[] = [
  {
    id: "meta-ads-expert",
    title: "Meta Ads Expert",
    icon: "📱",
    description: "Facebook & Instagram advertising campaigns, audience targeting, optimization",
    duration: "50-60 min",
    difficulty: "Advanced"
  },
  {
    id: "google-ads-expert", 
    title: "Google Ads Expert",
    icon: "🔍",
    description: "Search campaigns, keyword strategy, Quality Score optimization",
    duration: "50-60 min",
    difficulty: "Advanced"
  },
  {
    id: "shopify-developer",
    title: "Shopify Developer", 
    icon: "🛒",
    description: "Liquid templates, theme development, app integration, store optimization",
    duration: "50-60 min",
    difficulty: "Technical"
  },
  {
    id: "copywriter",
    title: "Copywriter",
    icon: "✍️", 
    description: "Ad copy, email marketing, landing pages, brand voice & messaging",
    duration: "50-60 min",
    difficulty: "Creative"
  },
  {
    id: "performance-marketing-manager",
    title: "Performance Marketing Manager",
    icon: "📊",
    description: "Multi-channel attribution, funnel optimization, ROI management",
    duration: "50-60 min", 
    difficulty: "Strategic"
  },
  {
    id: "social-media-intern",
    title: "Social Media Intern",
    icon: "📲",
    description: "Content planning, community management, platform best practices",
    duration: "50-60 min",
    difficulty: "Entry Level"
  },
  {
    id: "client-servicing-executive",
    title: "Client Servicing Executive",
    icon: "🤝",
    description: "Account management, client communication, conflict resolution",
    duration: "50-60 min",
    difficulty: "Interpersonal"
  },
  {
    id: "content-creator-ugc",
    title: "Content Creator / UGC Editor", 
    icon: "🎬",
    description: "Video editing, content strategy, trend analysis, UGC campaigns",
    duration: "50-60 min",
    difficulty: "Creative"
  }
];

interface RoleSelectionProps {
  onRoleSelect: (roleId: string, roleTitle: string) => void;
}

export default function RoleSelection({ onRoleSelect }: RoleSelectionProps) {
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  return (
    <div
      style={{
        width: "100%",
        maxWidth: 1200,
        padding: "40px 20px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 40
      }}
    >
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 20 }}>
        <h1
          style={{
            fontSize: 48,
            fontWeight: 800,
            margin: 0,
            marginBottom: 16,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          🎯 Choose Your Interview Role
        </h1>
        <p
          style={{
            fontSize: 20,
            color: "rgba(0,0,0,0.7)",
            margin: 0,
            fontWeight: 500
          }}
        >
          Select the position you'd like to practice interviewing for
        </p>
      </div>

      {/* Role Cards Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: 24,
          width: "100%",
        }}
      >
        {roles.map((role) => (
          <div
            key={role.id}
            onClick={() => onRoleSelect(role.id, role.title)}
            onMouseEnter={() => setHoveredCard(role.id)}
            onMouseLeave={() => setHoveredCard(null)}
            style={{
              background: "rgba(255,255,255,0.1)",
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
              borderRadius: 24,
              border: "1px solid rgba(255,255,255,0.2)",
              padding: 32,
              cursor: "pointer",
              transition: "all 0.3s ease",
              boxShadow: hoveredCard === role.id 
                ? "0 20px 60px rgba(102,126,234,0.2), inset 0 1px 0 rgba(255,255,255,0.3)"
                : "0 10px 40px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.2)",
              transform: hoveredCard === role.id ? "translateY(-8px)" : "translateY(0)",
              position: "relative" as const,
              overflow: "hidden"
            }}
          >
            {/* Hover Gradient Overlay */}
            {hoveredCard === role.id && (
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: "linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%)",
                  borderRadius: 24,
                  pointerEvents: "none"
                }}
              />
            )}

            {/* Card Content */}
            <div style={{ position: "relative", zIndex: 1 }}>
              {/* Icon & Title */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  marginBottom: 16
                }}
              >
                <div
                  style={{
                    fontSize: 40,
                    width: 60,
                    height: 60,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    borderRadius: 16,
                    boxShadow: "0 8px 24px rgba(102,126,234,0.3)"
                  }}
                >
                  {role.icon}
                </div>
                <h3
                  style={{
                    fontSize: 22,
                    fontWeight: 700,
                    margin: 0,
                    color: "#1a1a1a",
                    lineHeight: 1.2
                  }}
                >
                  {role.title}
                </h3>
              </div>

              {/* Description */}
              <p
                style={{
                  fontSize: 16,
                  color: "rgba(0,0,0,0.7)",
                  lineHeight: 1.5,
                  margin: "0 0 20px 0",
                  minHeight: 48
                }}
              >
                {role.description}
              </p>

              {/* Metadata */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  paddingTop: 16,
                  borderTop: "1px solid rgba(0,0,0,0.1)"
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontSize: 14, color: "rgba(0,0,0,0.6)" }}>⏱️ {role.duration}</span>
                </div>
                <div
                  style={{
                    padding: "6px 12px",
                    borderRadius: 12,
                    fontSize: 12,
                    fontWeight: 600,
                    background: "linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%)",
                    color: "#4c51bf",
                    border: "1px solid rgba(102,126,234,0.3)"
                  }}
                >
                  {role.difficulty}
                </div>
              </div>
            </div>

            {/* Hover Arrow */}
            {hoveredCard === role.id && (
              <div
                style={{
                  position: "absolute",
                  top: 24,
                  right: 24,
                  fontSize: 24,
                  color: "#667eea",
                  animation: "bounce 1s ease-in-out infinite"
                }}
              >
                →
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer Note */}
      <div
        style={{
          textAlign: "center",
          color: "rgba(0,0,0,0.6)",
          fontSize: 16,
          fontStyle: "italic",
          marginTop: 20
        }}
      >
        💡 Each interview is tailored to the specific role requirements and industry standards
      </div>

      {/* CSS Animations */}
      <style>
        {`
          @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateX(0); }
            40% { transform: translateX(4px); }
            60% { transform: translateX(2px); }
          }
        `}
      </style>
    </div>
  );
}
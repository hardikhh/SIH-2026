import React from "react";
import { ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div>
          <p style={{ fontWeight: 700, color: "#fff", marginBottom: "4px" }}>
            PM-AJAY (Pradhan Mantri Anusuchit Jaati Abhyuday Yojana) - Grant-in-Aid (GIA) Skilling
          </p>
          <p>
            Developed for Smart India Hackathon 2026 • Problem Statement ID: 26097
          </p>
          <p style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "4px" }}>
            Verified NSQF levels aligned with National Skill Development Corporation (NSDC) and Ministry of Social Justice & Empowerment.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <span style={{ display: "flex", alignItems: "center", gap: "0.3rem", color: "#10b981", fontWeight: 600 }}>
            <ShieldCheck size={16} /> Explainable AI & Rule-Based Guarantee
          </span>
        </div>
      </div>
    </footer>
  );
}

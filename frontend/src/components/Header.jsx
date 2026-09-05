import React from "react";
import { Mic, BarChart3, Radio, Globe, ShieldCheck } from "lucide-react";
import { translations } from "../utils/translations";

export default function Header({ currentLang, setLang, currentTab, setTab }) {
  const t = translations[currentLang] || translations.hi;

  return (
    <header className="app-header">
      <div className="gov-tricolor-strip" />
      <div className="header-content">
        <div className="brand-section">
          <div className="brand-emblem-badge" title="Government of India PM-AJAY">
            🇮🇳
          </div>
          <div className="brand-titles">
            <h1>{t.portalName}</h1>
            <p>{t.ministryName} • <span style={{ color: "var(--saffron-primary)", fontWeight: 700 }}>PS ID: 26097</span></p>
          </div>
        </div>

        <div className="nav-controls">
          <div className="view-tabs">
            <button
              id="tab-voice-btn"
              className={`tab-btn ${currentTab === "voice" ? "active" : ""}`}
              onClick={() => setTab("voice")}
            >
              <Mic size={16} />
              <span>{t.tabVoice}</span>
            </button>
            <button
              id="tab-admin-btn"
              className={`tab-btn ${currentTab === "admin" ? "active" : ""}`}
              onClick={() => setTab("admin")}
            >
              <BarChart3 size={16} />
              <span>{t.tabAdmin}</span>
            </button>
            <button
              id="tab-lowtech-btn"
              className={`tab-btn ${currentTab === "lowtech" ? "active" : ""}`}
              onClick={() => setTab("lowtech")}
            >
              <Radio size={16} />
              <span>{t.tabLowTech}</span>
            </button>
          </div>

          <div className="lang-selector">
            <button
              id="lang-hi-btn"
              className={`lang-btn ${currentLang === "hi" ? "active" : ""}`}
              onClick={() => setLang("hi")}
            >
              हिंदी
            </button>
            <button
              id="lang-gu-btn"
              className={`lang-btn ${currentLang === "gu" ? "active" : ""}`}
              onClick={() => setLang("gu")}
            >
              ગુજરાતી
            </button>
            <button
              id="lang-en-btn"
              className={`lang-btn ${currentLang === "en" ? "active" : ""}`}
              onClick={() => setLang("en")}
            >
              English
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

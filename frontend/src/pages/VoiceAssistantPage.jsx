import React, { useState, useEffect, useRef } from "react";
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  Store,
  MapPin,
  Sparkles,
  Award,
  BookOpen,
  ArrowRight,
  PhoneCall,
  ShieldCheck,
  Download
} from "lucide-react";
import { translations } from "../utils/translations";
import { speechService } from "../services/speechService";
import { api } from "../services/api";
import LivelihoodCardModal from "../components/LivelihoodCardModal";

const DEMO_PERSONAS = [
  {
    id: "persona-ramesh",
    label: "⚡ रमेश (सोलर / इलेक्ट्रीशियन)",
    badge: "ग्रीन जॉब्स",
    profile: {
      name: "Ramesh Solanki",
      education_level: "10th Pass",
      existing_skills: ["basic electrical work", "hand tool usage", "physical fitness"],
      interests: ["solar systems", "electrical appliances"],
      work_experience_years: 2.0,
      livelihood_preference: "Both",
      has_mobility_constraint: false,
      location_district: "Ahmedabad"
    },
    message: "मेरा नाम रमेश सोलंकी है, मैं 10वीं पास हूँ। मैंने 2 साल बिजली की दुकान में काम किया है और मैं सोलर पैनल का नया काम सीखना चाहता हूँ।"
  },
  {
    id: "persona-sunita",
    label: "🧵 सुनीता (महिला SHG सिलाई)",
    badge: "महिला स्वरोजगार",
    profile: {
      name: "Sunita Vaghela",
      education_level: "8th Pass",
      existing_skills: ["hand needlework", "cloth cutting", "color matching"],
      interests: ["sewing", "fashion and clothing", "home business"],
      work_experience_years: 3.5,
      livelihood_preference: "Self Employment",
      has_mobility_constraint: false,
      location_district: "Ahmedabad"
    },
    message: "मेरा नाम सुनीता है, मैंने 8वीं तक पढ़ाई की है। मुझे हाथ से सिलाई का काम आता है और मुझे अपनी सिलाई की दुकान खोलने के लिए सरकारी अनुदान चाहिए।"
  },
  {
    id: "persona-dinesh",
    label: "♿ दिनेश (दिव्यांगता समावेशी)",
    badge: "PwD अनुकूल",
    profile: {
      name: "Dinesh Rathod",
      education_level: "Below 8th",
      existing_skills: ["hand tool usage", "patience and record keeping"],
      interests: ["mushroom cultivation", "mobile phones", "electronics repair"],
      work_experience_years: 5.0,
      livelihood_preference: "Self Employment",
      has_mobility_constraint: true,
      max_travel_distance_km: 5,
      location_district: "Ahmedabad"
    },
    message: "मेरा नाम दिनेश है, पैर में चोट लगने के कारण मैं ज्यादा चल-फिर या वजन नहीं उठा सकता। मुझे घर बैठकर या पास में कोई हल्का हुनर सीखना है।"
  },
  {
    id: "persona-prakash",
    label: "📱 प्रकाश (युवा टेक / CCTV)",
    badge: "12वीं पास टेक",
    profile: {
      name: "Prakash Parmar",
      education_level: "12th Pass",
      existing_skills: ["basic computer literacy", "wire twisting", "hand tool usage"],
      interests: ["mobile phones", "security cameras", "gadget repair"],
      work_experience_years: 1.0,
      livelihood_preference: "Wage Employment",
      has_mobility_constraint: false,
      location_state: "Gujarat",
      location_district: "Vadodara",
      full_address: "GIDC Industrial Area, Savli, Vadodara - 391775",
      pincode: "391775"
    },
    message: "मेरा नाम प्रकाश है, मैं 12वीं पास हूँ और मुझे मोबाइल रिपेयरिंग या CCTV इंस्टॉलेशन सीखकर किसी अच्छी कंपनी में नौकरी करनी है।"
  },
  {
    id: "persona-surendra-rj",
    label: "☀️ सुरेंद्र (राजस्थान सोलर)",
    badge: "राजस्थान सोलर हब",
    profile: {
      name: "Surendra Meghwal",
      education_level: "10th Pass",
      existing_skills: ["basic electrical work", "hand tool usage", "physical fitness"],
      interests: ["solar systems", "green energy"],
      work_experience_years: 2.0,
      livelihood_preference: "Both",
      has_mobility_constraint: false,
      location_state: "Rajasthan",
      location_district: "Jodhpur",
      full_address: "RIICO Boronada Phase 2, Jodhpur, Rajasthan - 342012",
      pincode: "342012"
    },
    message: "मेरा नाम सुरेंद्र मेघवाल है, मैं जोधपुर राजस्थान का रहने वाला हूँ। मैंने बिजली का थोड़ा काम किया है और मैं सोलर पार्क में सोलर पैनल की ट्रेनिंग लेना चाहता हूँ।"
  }
];

export default function VoiceAssistantPage({ currentLang }) {
  const t = translations[currentLang] || translations.hi;

  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState([]);
  const [profileData, setProfileData] = useState({
    education_level: null,
    existing_skills: [],
    interests: [],
    livelihood_preference: null,
    work_experience_years: 0,
    has_mobility_constraint: false,
    location_state: null,
    location_district: null,
    location_block: null,
    full_address: null,
    pincode: null
  });
  const [beneficiaryId, setBeneficiaryId] = useState(null);
  const [quickReplies, setQuickReplies] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [enrollmentStatus, setEnrollmentStatus] = useState(null);
  const [isCardModalOpen, setIsCardModalOpen] = useState(false);

  const dialogueEndRef = useRef(null);

  const handleSelectPersona = (persona) => {
    setProfileData(persona.profile);
    setMessages([
      { role: "assistant", content: `नमस्ते ${persona.profile.name}! आपका प्रोफाइल लाइव लोड हो गया है।` },
      { role: "user", content: persona.message }
    ]);
    fetchRecommendations(persona.profile);
  };

  // Update welcome message text and speak greeting aloud
  useEffect(() => {
    let active = true;
    speechService.stopSpeaking();
    setIsSpeaking(false);

    async function loadWelcome() {
      try {
        const res = await api.getWelcomePrompt(currentLang);
        if (active) {
          setMessages([
            { role: "assistant", content: res.welcome_message }
          ]);
          setQuickReplies(res.suggested_quick_replies || []);

          // Speak welcome message aloud
          setIsSpeaking(true);
          speechService.speak(res.welcome_message, currentLang, () => {
            if (active) setIsSpeaking(false);
          });
        }
      } catch (err) {
        if (active) {
          const defaultMsg = t.voiceHeroSub;
          setMessages([{ role: "assistant", content: defaultMsg }]);
          setIsSpeaking(true);
          speechService.speak(defaultMsg, currentLang, () => {
            if (active) setIsSpeaking(false);
          });
        }
      }
    }
    loadWelcome();
    return () => {
      active = false;
      speechService.stopSpeaking();
      speechService.stopListening();
    };
  }, [currentLang]);

  useEffect(() => {
    dialogueEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle voice speech recognition
  const toggleListening = () => {
    if (isListening) {
      speechService.stopListening();
      setIsListening(false);
    } else {
      speechService.stopSpeaking();
      setIsSpeaking(false);
      setIsListening(true);

      speechService.startListening(
        currentLang,
        (transcript) => {
          setIsListening(false);
          handleSendMessage(transcript);
        },
        (error) => {
          setIsListening(false);
          console.warn("Speech recognition error:", error);
        },
        () => {
          setIsListening(false);
        }
      );
    }
  };

  // Send message turn to backend
  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputText).trim();
    if (!text) return;

    setInputText("");
    const newMessages = [...messages, { role: "user", content: text }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await api.sendVoiceTurn({
        beneficiary_id: beneficiaryId,
        user_message: text,
        language: currentLang,
        conversation_history: newMessages,
        current_profile: profileData,
      });

      setBeneficiaryId(response.beneficiary_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.ai_response }
      ]);
      setQuickReplies(response.suggested_quick_replies || []);

      if (response.profile_data) {
        setProfileData((prev) => ({
          ...prev,
          ...response.profile_data
        }));
      }

      // Speak assistant response
      setIsSpeaking(true);
      speechService.speak(response.ai_response, currentLang, () => {
        setIsSpeaking(false);
      });

      // If profile is complete, fetch top recommendations!
      if (response.is_profile_complete) {
        fetchRecommendations(response.profile_data || profileData);
      }
    } catch (err) {
      console.error("Failed to send voice turn:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "क्षमा करें, सर्वर से संपर्क नहीं हो पाया। कृपया पुनः प्रयास करें।"
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch recommendations for current profile
  const fetchRecommendations = async (profile) => {
    setIsLoading(true);
    try {
      const payload = profile || profileData;
      const res = await api.evaluateDirect({
        ...payload,
        language_preference: currentLang,
      });
      setRecommendations(res.recommendations || []);
    } catch (err) {
      console.error("Failed to evaluate recommendations:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate profile completion percentage (20% each for Location, Education, Skills, Interests, Preference)
  const calculateProgress = () => {
    let score = 0;
    if (profileData.location_district) score += 20;
    if (profileData.education_level) score += 20;
    if (profileData.existing_skills && profileData.existing_skills.length > 0) score += 20;
    if (profileData.interests && profileData.interests.length > 0) score += 20;
    if (profileData.livelihood_preference) score += 20;
    return score;
  };

  const progress = calculateProgress();

  const handleEnroll = (trade) => {
    setEnrollmentStatus(`सफलतापूर्वक पंजीकृत! ${trade.trade_title} के लिए आपके विवरण निकटतम पीएम-अजय कौशल केंद्र को भेज दिए गए हैं। फील्ड अधिकारी शीघ्र संपर्क करेंगे।`);
    setTimeout(() => setEnrollmentStatus(null), 8000);
  };

  return (
    <div className="voice-assistant-page">
      {/* Alert toast */}
      {enrollmentStatus && (
        <div style={{
          background: "#ecfdf5",
          border: "1px solid #10b981",
          color: "#065f46",
          padding: "1rem",
          borderRadius: "12px",
          marginBottom: "1.5rem",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          fontWeight: 600
        }}>
          <CheckCircle2 size={20} />
          <span>{enrollmentStatus}</span>
        </div>
      )}

      {/* 1-Click Demo Personas Bar for SIH Jury Presentation */}
      <div style={{
        background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
        border: "1px solid #e2e8f0",
        borderRadius: "14px",
        padding: "0.85rem 1.25rem",
        marginBottom: "1.25rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.04)"
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.6rem" }}>
          <span style={{ fontSize: "0.82rem", fontWeight: 800, color: "#ea580c", display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <Sparkles size={16} /> 1-क्लिक जूरी डेमो प्रोफाइल (SIH Pitch Shortcuts):
          </span>
          <span style={{ fontSize: "0.72rem", color: "#64748b" }}>
            क्लिक करके लाइव सिफारिशें व कौशल अंतर तुरंत देखें
          </span>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {DEMO_PERSONAS.map((p) => (
            <button
              key={p.id}
              id={p.id}
              onClick={() => handleSelectPersona(p)}
              style={{
                background: "#ffffff",
                border: "1px solid #cbd5e1",
                borderRadius: "20px",
                padding: "0.45rem 0.9rem",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "0.45rem",
                transition: "all 0.2s ease"
              }}
            >
              <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "#0f172a" }}>{p.label}</span>
              <span style={{
                fontSize: "0.68rem",
                fontWeight: 700,
                background: "#ffedd5",
                color: "#c2410c",
                padding: "1px 6px",
                borderRadius: "10px"
              }}>
                {p.badge}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Voice Hero Card */}
      <section className="voice-hero-card">
        <div className="voice-hero-content">
          <div className="gov-badge">
            <Sparkles size={14} />
            <span>{t.badgeGIA}</span>
          </div>
          <h2 className="voice-hero-title">{t.voiceHeroTitle}</h2>
          <p className="voice-hero-sub">{t.voiceHeroSub}</p>

          {/* Big Pulsing Mic Button */}
          <div className="mic-action-container">
            <button
              id="voice-record-btn"
              className={`big-mic-button ${isListening ? "listening" : ""}`}
              onClick={toggleListening}
              title={isListening ? "Listening... Click to stop" : "Click to speak"}
            >
              {isListening ? <MicOff size={42} /> : <Mic size={42} />}
            </button>

            <div className="mic-status-label">
              {isListening ? (
                <>
                  <span style={{ color: "#ef4444" }}>●</span>
                  <span>{t.listening}</span>
                  <div className="wave-bars-container">
                    <div className="wave-bar" />
                    <div className="wave-bar" />
                    <div className="wave-bar" />
                    <div className="wave-bar" />
                    <div className="wave-bar" />
                  </div>
                </>
              ) : isSpeaking ? (
                <>
                  <Volume2 size={18} color="#fb923c" />
                  <span>{t.speaking}</span>
                </>
              ) : isLoading ? (
                <span>{t.aiThinking}</span>
              ) : (
                <span>{t.tapToSpeak}</span>
              )}
            </div>

            <button
              id="listen-welcome-greeting-btn"
              className="welcome-speech-trigger-btn"
              onClick={() => {
                const welcomeMsg = messages[0]?.content || "नमस्ते! मैं आपका पीएम-अजय आजीविका एवं कौशल साथी हूँ।";
                setIsSpeaking(true);
                speechService.stopSpeaking();
                speechService.speak(welcomeMsg, currentLang, () => setIsSpeaking(false));
              }}
              style={{
                marginTop: "0.5rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                background: "rgba(251, 146, 60, 0.12)",
                border: "1px solid rgba(251, 146, 60, 0.35)",
                color: "#fb923c",
                padding: "5px 14px",
                borderRadius: "20px",
                fontSize: "0.8rem",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
              title="स्वागत संदेश आवाज में सुनें"
            >
              <Volume2 size={14} />
              <span>
                {currentLang === "gu"
                  ? "સ્વાગત અવાજ સાંભળો"
                  : currentLang === "hi"
                  ? "स्वागत संदेश सुनें"
                  : "Listen Welcome"}
              </span>
            </button>
          </div>

          {/* Quick Replies */}
          {quickReplies.length > 0 && (
            <div className="quick-replies-tray">
              {quickReplies.map((reply, idx) => (
                <button
                  key={idx}
                  className="reply-chip"
                  onClick={() => handleSendMessage(reply)}
                >
                  {reply}
                </button>
              ))}
            </div>
          )}

          {/* Dialogue Conversation Stream */}
          <div className="dialogue-stream">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`chat-bubble ${msg.role === "assistant" ? "ai" : "user"}`}
              >
                <div className="bubble-avatar">
                  {msg.role === "assistant" ? "AI" : "YOU"}
                </div>
                <div className="bubble-body">
                  <div>{msg.content}</div>
                  {msg.role === "assistant" && (
                    <button
                      className="bubble-listen-btn"
                      onClick={() => {
                        setIsSpeaking(true);
                        speechService.stopSpeaking();
                        speechService.speak(msg.content, currentLang, () => setIsSpeaking(false));
                      }}
                      style={{
                        background: "none",
                        border: "none",
                        color: "#fb923c",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                        fontSize: "0.72rem",
                        marginTop: "5px",
                        padding: "2px 0"
                      }}
                      title="आवाज सुनें"
                    >
                      <Volume2 size={13} />
                      <span>{currentLang === "gu" ? "સાંભળો" : currentLang === "hi" ? "आवाज सुनें" : "Listen"}</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
            <div ref={dialogueEndRef} />
          </div>

          {/* Text input fallback */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            style={{ display: "flex", gap: "0.5rem", width: "100%", marginTop: "1rem" }}
          >
            <input
              id="voice-text-fallback-input"
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="या यहाँ लिखकर भेजें (e.g. 10वीं पास, सिलाई का काम आता है)..."
              style={{
                flex: 1,
                padding: "0.75rem 1rem",
                borderRadius: "var(--radius-md)",
                border: "1px solid rgba(255,255,255,0.2)",
                background: "rgba(15,23,42,0.6)",
                color: "#ffffff",
                fontSize: "0.9rem"
              }}
            />
            <button
              id="voice-text-send-btn"
              type="submit"
              className="btn-primary"
              style={{ flex: "none", width: "48px", padding: 0 }}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </section>

      {/* Profile Completeness Meter with Location & Address Verification */}
      <section className="profile-progress-widget">
        <div className="progress-info">
          <h4>{t.profileProgressTitle} ({progress}% पूर्ण)</h4>
          <p style={{ marginTop: "3px" }}>
            स्थान: {profileData.location_district ? (
              <strong style={{ color: "#ea580c" }}>{profileData.location_district}, {profileData.location_state || ""} {profileData.pincode ? `(${profileData.pincode})` : ""}</strong>
            ) : (
              <strong style={{ color: "#ef4444" }}>पूछना बाकी (जिला / राज्य / पिनकोड)</strong>
            )} | 
            शिक्षा: <strong>{profileData.education_level || "पूछना बाकी"}</strong> | 
            हुनर: <strong>{profileData.existing_skills?.join(", ") || "पूछना बाकी"}</strong>
          </p>
          {profileData.full_address && (
            <p style={{ fontSize: "0.78rem", color: "#64748b", margin: "2px 0 0 0" }}>
              📍 पता: <em>{profileData.full_address}</em>
            </p>
          )}
        </div>
        <div className="progress-bar-track">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>
        <button
          id="btn-evaluate-now"
          className="btn-secondary"
          onClick={() => fetchRecommendations()}
          title="तुरंत सिफारिशें देखें"
        >
          <Sparkles size={16} />
          <span>सिफारिशें देखें</span>
        </button>
      </section>

      {/* Top 3 Recommendations Section */}
      {recommendations.length > 0 && (
        <section className="recommendations-section">
          {/* Official PM-AJAY Livelihood Card Banner */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background: "linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)",
            border: "2px solid #fb923c",
            borderRadius: "var(--radius-lg)",
            padding: "1.1rem 1.5rem",
            marginBottom: "1.5rem",
            boxShadow: "0 6px 16px rgba(251, 146, 60, 0.18)",
            flexWrap: "wrap",
            gap: "1rem"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
              <div style={{
                background: "#ea580c",
                color: "#ffffff",
                width: "46px",
                height: "46px",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0
              }}>
                <ShieldCheck size={26} />
              </div>
              <div>
                <h4 style={{ margin: 0, color: "#9a3412", fontSize: "1.05rem", fontWeight: 800 }}>
                  {currentLang === "gu"
                    ? "સત્તાવાર પીએમ-અજય આજીવિકા સંસ્તુતિ કાર્ડ ઉપલબ્ધ છે!"
                    : currentLang === "hi"
                    ? "आधिकारिक पीएम-अजय आजीविका संस्तुति पत्र (QR कार्ड) तैयार है!"
                    : "Official PM-AJAY Livelihood Recommendation Card Ready!"}
                </h4>
                <p style={{ margin: 0, fontSize: "0.82rem", color: "#c2410c", marginTop: "2px" }}>
                  {currentLang === "gu"
                    ? "જિલ્લા કલ્યાણ કચેરી અને ₹૫૦,૦૦૦ અનુદાન માટે સત્તાવાર QR કોડ સ્લિપ ડાઉનલોડ કરો"
                    : currentLang === "hi"
                    ? "जिला समाज कल्याण कार्यालय एवं ₹50,000 अनुदान सत्यापन हेतु आधिकारिक QR स्लिप डाउनलोड करें"
                    : "Official verified slip with QR verification for District Welfare Office & ₹50,000 Grant"}
                </p>
              </div>
            </div>

            <button
              id="btn-download-livelihood-card"
              onClick={() => setIsCardModalOpen(true)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "0.75rem 1.4rem",
                fontSize: "0.92rem",
                fontWeight: 800,
                background: "#ea580c",
                border: "none",
                borderRadius: "var(--radius-md)",
                color: "#ffffff",
                boxShadow: "0 4px 14px rgba(234, 88, 12, 0.35)",
                cursor: "pointer",
                transition: "transform 0.15s, background 0.15s"
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = "#c2410c"}
              onMouseLeave={(e) => e.currentTarget.style.background = "#ea580c"}
            >
              <Download size={18} />
              <span>
                {currentLang === "gu"
                  ? "આજીવિકા કાર્ડ ડાઉનલોડ / પ્રિન્ટ (PDF / QR)"
                  : currentLang === "hi"
                  ? "आजीविका कार्ड डाउनलोड / प्रिंट (PDF / QR)"
                  : "Download / Print Livelihood Card"}
              </span>
            </button>
          </div>

          <div className="section-heading">
            <h2>
              <Award size={24} color="var(--saffron-primary)" />
              {t.topRecommendations}
            </h2>
            <p>{t.topRecommendationsSub}</p>
          </div>

          <div className="recommendations-grid">
            {recommendations.map((rec) => {
              const displayTitle = currentLang === "hi" && rec.trade_title_hi
                ? rec.trade_title_hi
                : currentLang === "gu" && rec.trade_title_gu
                ? rec.trade_title_gu
                : rec.trade_title;

              const displayExplanation = currentLang === "hi"
                ? rec.explanation_hi
                : currentLang === "gu"
                ? rec.explanation_gu
                : rec.explanation_en;

              return (
                <div key={rec.job_role_id} className="recommendation-card">
                  <div>
                    <div className="card-top-header">
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span className={`rank-badge ${rec.rank === 1 ? "gold" : ""}`}>
                          #{rec.rank}
                        </span>
                        <span className="nsqf-level-badge">
                          {t.nsqfLevel} {rec.nsqf_level}
                        </span>
                      </div>
                      <div className="match-score-badge">
                        <span>{rec.overall_match_score}%</span>
                      </div>
                    </div>

                    <h3 className="trade-title">{displayTitle}</h3>
                    <p className="trade-sector">{rec.sector}</p>

                    <div className="trade-explanation">
                      <p>{displayExplanation}</p>
                      <button
                        className="btn-secondary"
                        style={{ marginTop: "0.5rem", padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
                        onClick={() => {
                          setIsSpeaking(true);
                          speechService.stopSpeaking();
                          speechService.speak(displayExplanation, currentLang, () => setIsSpeaking(false));
                        }}
                      >
                        <Volume2 size={14} />
                        <span>{t.listenAudio}</span>
                      </button>
                    </div>

                    {/* Skill Gap Pills */}
                    <div className="skill-gap-summary">
                      {rec.skill_gap.matching_skills.length > 0 && (
                        <div className="gap-group">
                          <span className="gap-group-label">
                            ✓ {t.matchingSkills}
                          </span>
                          <div className="pills-container">
                            {rec.skill_gap.matching_skills.map((s, i) => (
                              <span key={i} className="skill-pill matching">
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="gap-group">
                        <span className="gap-group-label">
                          ⚡ {t.missingSkills} ({rec.training_duration_hours} घंटे ट्रेनिंग)
                        </span>
                        <div className="pills-container">
                          {rec.skill_gap.missing_skills.slice(0, 4).map((s, i) => (
                            <span key={i} className="skill-pill missing">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Dual Pathways */}
                    <div className="pathways-box">
                      <div className="pathway-col">
                        <span className="label">
                          <Briefcase size={12} /> {t.wageRoute}
                        </span>
                        <span className="val">{rec.wage_route.starting_salary_range}</span>
                        <span style={{ fontSize: "0.7rem", color: "#64748b" }}>
                          {rec.wage_route.job_role}
                        </span>
                      </div>
                      <div className="pathway-col">
                        <span className="label">
                          <Store size={12} /> {t.selfEmpRoute}
                        </span>
                        <span className="val" style={{ color: "#047857" }}>
                          {rec.self_employment_route.pm_ajay_grant_support}
                        </span>
                        <span style={{ fontSize: "0.7rem", color: "#64748b" }}>
                          {rec.self_employment_route.estimated_monthly_income}
                        </span>
                      </div>
                    </div>

                    {/* Nearby Training Center */}
                    {rec.nearby_training_centers.length > 0 && (
                      <div style={{
                        background: "#f8fafc",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                        padding: "0.65rem",
                        marginBottom: "0.6rem",
                        fontSize: "0.78rem"
                      }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontWeight: 700, color: "#0f172a" }}>
                          <MapPin size={14} color="#ea580c" />
                          <span>{t.nearbyCenter}: {rec.nearby_training_centers[0].name}</span>
                        </div>
                        {rec.nearby_training_centers[0].address && (
                          <div style={{ color: "#475569", fontSize: "0.74rem", marginTop: "2px" }}>
                            🏢 {rec.nearby_training_centers[0].address}
                          </div>
                        )}
                        <p style={{ color: "#64748b", marginTop: "2px", marginBottom: 0 }}>
                          दूरी: ~{rec.nearby_training_centers[0].distance_km} किमी • 
                          सीटें: {rec.nearby_training_centers[0].available_seats} • 
                          निःशुल्क स्टाइपेंड: ₹{rec.nearby_training_centers[0].free_daily_stipend_inr}/दिन •
                          {rec.nearby_training_centers[0].phone && ` 📞 ${rec.nearby_training_centers[0].phone}`}
                        </p>
                      </div>
                    )}

                    {/* Local Verified Job Vacancies near Beneficiary */}
                    {rec.local_vacancies && rec.local_vacancies.length > 0 && (
                      <div style={{
                        background: "rgba(16, 185, 129, 0.06)",
                        border: "1px solid rgba(16, 185, 129, 0.25)",
                        borderRadius: "8px",
                        padding: "0.6rem",
                        marginBottom: "1rem",
                        fontSize: "0.76rem"
                      }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontWeight: 700, color: "#065f46", marginBottom: "3px" }}>
                          <Briefcase size={13} color="#059669" />
                          <span>नज़दीकी भर्ती अवसर ({rec.local_vacancies[0].district}): {rec.local_vacancies[0].openings} पद उपलब्ध</span>
                        </div>
                        <div style={{ color: "#0f172a", fontWeight: 600 }}>
                          {rec.local_vacancies[0].title} — <span style={{ color: "#059669" }}>{rec.local_vacancies[0].stipend_or_salary}</span>
                        </div>
                        <div style={{ color: "#64748b", fontSize: "0.72rem", marginTop: "1px" }}>
                          नियोक्ता: {rec.local_vacancies[0].employer} {rec.local_vacancies[0].transport_provided ? "• वाहन सुविधा उपलब्ध" : ""}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="card-actions">
                    <button
                      className="btn-primary"
                      onClick={() => handleEnroll(rec)}
                    >
                      <ArrowRight size={16} />
                      <span>{t.applyNow}</span>
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => handleEnroll(rec)}
                      title="सहायक से संपर्क करें"
                    >
                      <PhoneCall size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Official PM-AJAY Livelihood & Skilling Recommendation Slip Modal */}
      <LivelihoodCardModal
        isOpen={isCardModalOpen}
        onClose={() => setIsCardModalOpen(false)}
        beneficiary={profileData}
        topRecommendation={recommendations[0]}
        language={currentLang}
      />
    </div>
  );
}

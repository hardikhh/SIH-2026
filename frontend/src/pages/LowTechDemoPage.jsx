import React, { useState } from "react";
import { Phone, MessageSquare, Monitor, Volume2, CheckCircle2, Shield } from "lucide-react";
import { speechService } from "../services/speechService";

export default function LowTechDemoPage({ currentLang }) {
  // IVR State
  const [ivrStep, setIvrStep] = useState(0);
  const [ivrStatus, setIvrStatus] = useState("कॉल करने के लिए '1800-11-AJAY' डायल करें");
  const [callActive, setCallActive] = useState(false);

  // WhatsApp State
  const [waAudioPlayed, setWaAudioPlayed] = useState(false);

  // Handle IVR Keypad press
  const handleKeypadPress = (digit) => {
    if (!callActive) {
      setCallActive(true);
      setIvrStep(1);
      const text = "नमस्ते, पीएम-अजय निःशुल्क आजीविका हेल्पलाइन में आपका स्वागत है। हिंदी के लिए 1 दबाएं, गुजराती माटे 2 दबावो।";
      setIvrStatus(text);
      speechService.speak(text, "hi");
      return;
    }

    if (ivrStep === 1) {
      if (digit === "1") {
        setIvrStep(2);
        const text = "आपने हिंदी चुनी है। सोलर तकनीशियन के लिए 1 दबाएं, घरेलू इलेक्ट्रीशियन के लिए 2 दबाएं, सिलाई कार्य के लिए 3 दबाएं।";
        setIvrStatus(text);
        speechService.speak(text, "hi");
      } else if (digit === "2") {
        setIvrStep(2);
        const text = "તમે ગુજરાતી પસંદ કરી છે. સોલર ટેકનિશિયન માટે 1, ઇલેક્ટ્રિશિયન માટે 2, દરજીકામ માટે 3 દબાવો.";
        setIvrStatus(text);
        speechService.speak(text, "gu");
      }
    } else if (ivrStep === 2) {
      setIvrStep(3);
      const text = "बहुत धन्यवाद! आपकी प्रोफाइल के अनुसार NSQF लेवल 4 सूर्यमित्र सोलर ट्रेनिंग और ₹50,000 पीएम-अजय टूलकिट ग्रांट की जानकारी आपके मोबाइल पर एसएमएस द्वारा भेज दी गई है।";
      setIvrStatus(text);
      speechService.speak(text, "hi");
    }
  };

  const handleEndCall = () => {
    speechService.stopSpeaking();
    setCallActive(false);
    setIvrStep(0);
    setIvrStatus("कॉल समाप्त। पुनः डायल करने के लिए कोई भी बटन दबाएं।");
  };

  return (
    <div className="low-tech-demo-page">
      <div className="section-heading">
        <h2>ग्रामीण एवं कम-तकनीकी चैनल प्रदर्शक (Low-Tech Deployment)</h2>
        <p>
          स्मार्टफोन या हाई-स्पीड इंटरनेट न होने पर भी अनुसूचित जाति के अंतिम व्यक्ति तक पहुंच सुनिश्चित करने की रूपरेखा
        </p>
      </div>

      <div className="low-tech-grid">
        {/* Channel 1: IVR Feature Phone Simulator */}
        <div className="channel-card">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <Phone size={20} color="#ea580c" />
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>1. IVR टोल-फ्री फोन सेवा (Toll-Free IVR)</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#64748b", marginBottom: "1rem" }}>
            सादे कीपैड वाले फीचर फोन से 1800-11-AJAY पर मिस्ड कॉल या बातचीत द्वारा ऑटोमेटेड वॉयस बॉट
          </p>

          <div className="phone-simulator-frame">
            <div className="phone-screen">
              <span style={{ fontSize: "0.72rem", color: "#94a3b8" }}>
                {callActive ? "● 00:32 (कॉल चालू)" : "PM-AJAY 1800-11-2529"}
              </span>
              <p style={{ fontSize: "0.8rem", color: "#f8fafc", lineHeight: 1.4 }}>
                {ivrStatus}
              </p>
            </div>

            <div className="keypad-grid">
              {["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"].map((d) => (
                <button
                  key={d}
                  className="keypad-btn"
                  onClick={() => handleKeypadPress(d)}
                >
                  {d}
                </button>
              ))}
            </div>

            <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
              <button
                className="btn-primary"
                style={{ flex: 1, background: "#10b981", fontSize: "0.8rem", padding: "0.5rem" }}
                onClick={() => handleKeypadPress("1")}
              >
                कॉल शुरू
              </button>
              <button
                className="btn-secondary"
                style={{ flex: 1, background: "#ef4444", color: "#fff", border: "none", fontSize: "0.8rem", padding: "0.5rem" }}
                onClick={handleEndCall}
              >
                कॉल काटें
              </button>
            </div>
          </div>
        </div>

        {/* Channel 2: WhatsApp Voice Notes Assistant */}
        <div className="channel-card">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <MessageSquare size={20} color="#10b981" />
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>2. व्हाट्सएप वॉयस नोट बॉट (WhatsApp Bot)</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#64748b", marginBottom: "1rem" }}>
            लाभार्थी केवल अपना 15 सेकंड का ऑडियो वॉयस मैसेज भेजते हैं और बॉट तुरंत प्रोफाइल कार्ड वापस भेजता है।
          </p>

          <div style={{
            background: "#0b141a",
            borderRadius: "16px",
            padding: "1rem",
            color: "#fff",
            maxWidth: "320px",
            margin: "0 auto",
            boxShadow: "var(--shadow-md)"
          }}>
            <div style={{ borderBottom: "1px solid #222d34", paddingBottom: "0.5rem", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: "#25d366", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>
                AJ
              </div>
              <div>
                <div style={{ fontSize: "0.85rem", fontWeight: 700 }}>PM-AJAY Livelihood Bot ✓</div>
                <div style={{ fontSize: "0.68rem", color: "#8696a0" }}>आधिकारिक सरकारी बॉट</div>
              </div>
            </div>

            {/* Incoming voice note */}
            <div style={{
              background: "#005c4b",
              borderRadius: "12px",
              padding: "0.65rem 0.85rem",
              marginBottom: "0.75rem",
              fontSize: "0.8rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <button
                  style={{ background: "none", border: "none", color: "#fff", cursor: "pointer" }}
                  onClick={() => {
                    speechService.speak("मेरा नाम कांतिभाई है, मैं 10वीं पास हूँ और मुझे सोलर का काम सीखना है", "hi");
                    setWaAudioPlayed(true);
                  }}
                >
                  <Volume2 size={16} />
                </button>
                <span>लाभार्थी वॉयस नोट (0:12s)</span>
              </div>
              <span style={{ fontSize: "0.65rem", color: "#8696a0" }}>10:42 AM ✓✓</span>
            </div>

            {/* Automated bot response card */}
            <div style={{
              background: "#202c33",
              borderRadius: "12px",
              padding: "0.75rem",
              fontSize: "0.78rem",
              lineHeight: 1.4
            }}>
              <p style={{ fontWeight: 700, color: "#25d366", marginBottom: "4px" }}>
                🎯 आपके लिए अनुशंसित योजना:
              </p>
              <p><strong>ट्रेड:</strong> सोलर पीवी इंस्टॉलर (सूर्यमित्र)</p>
              <p><strong>NSQF स्तर:</strong> Level 4 (निःशुल्क)</p>
              <p><strong>पीएम-अजय अनुदान:</strong> ₹50,000 टूलकिट सहायता</p>
              <p><strong>निकटतम केंद्र:</strong> अहमदाबाद नॉर्थ कौशल केंद्र</p>
              <div style={{ marginTop: "6px", display: "flex", gap: "4px" }}>
                <span style={{ background: "#005c4b", padding: "3px 6px", borderRadius: "4px", fontSize: "0.68rem" }}>
                  1 दबाकर रजिस्टर करें
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Channel 3: Gram Panchayat Kiosk Mode */}
        <div className="channel-card">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <Monitor size={20} color="#2563eb" />
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>3. ग्राम पंचायत कियोस्क (Village Kiosk Mode)</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#64748b", marginBottom: "1rem" }}>
            CSC केंद्र या ग्राम पंचायत टच-स्क्रीन के लिए बड़े बटन और दृश्य प्रतीकों वाला अल्ट्रा-एक्सेसिबल इंटरफ़ेस
          </p>

          <div style={{
            background: "#ffffff",
            border: "2px solid #2563eb",
            borderRadius: "14px",
            padding: "1rem",
            textAlign: "center"
          }}>
            <div style={{ background: "#dbeafe", color: "#1e40af", padding: "0.4rem", borderRadius: "8px", fontWeight: 700, fontSize: "0.85rem", marginBottom: "0.75rem" }}>
              ग्राम सुविधा केंद्र (CSC) - टच स्क्रीन
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
              <button
                className="btn-secondary"
                style={{ height: "60px", flexDirection: "column", fontSize: "0.8rem", fontWeight: 700 }}
                onClick={() => speechService.speak("सोलर और बिजली प्रशिक्षण के लिए स्क्रीन को छुएं", "hi")}
              >
                ⚡ सोलर / बिजली
              </button>
              <button
                className="btn-secondary"
                style={{ height: "60px", flexDirection: "column", fontSize: "0.8rem", fontWeight: 700 }}
                onClick={() => speechService.speak("सिलाई और गारमेंट प्रशिक्षण के लिए स्क्रीन को छुएं", "hi")}
              >
                🧵 सिलाई व बुनाई
              </button>
              <button
                className="btn-secondary"
                style={{ height: "60px", flexDirection: "column", fontSize: "0.8rem", fontWeight: 700 }}
                onClick={() => speechService.speak("डेयरी और पशुपालन प्रशिक्षण के लिए स्क्रीन को छुएं", "hi")}
              >
                🥛 डेयरी व खेती
              </button>
              <button
                className="btn-secondary"
                style={{ height: "60px", flexDirection: "column", fontSize: "0.8rem", fontWeight: 700 }}
                onClick={() => speechService.speak("वाहन रिपेयरिंग और ड्राइविंग के लिए स्क्रीन को छुएं", "hi")}
              >
                🛵 बाइक / ऑटो
              </button>
            </div>

            <button
              className="btn-primary"
              style={{ width: "100%", marginTop: "0.75rem", height: "46px" }}
              onClick={() => speechService.speak("ग्राम सहायक से संपर्क करने के लिए पर्ची प्रिंट हो रही है", "hi")}
            >
              वॉयस सहायता / पर्ची प्रिंट करें
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

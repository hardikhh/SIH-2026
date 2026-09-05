import React, { useEffect, useState, useRef } from "react";
import QRCode from "qrcode";
import { Printer, Share2, X, Download, ShieldCheck, Award, MapPin, Phone, Calendar, IndianRupee, Sparkles } from "lucide-react";

export default function LivelihoodCardModal({ isOpen, onClose, beneficiary, topRecommendation, language = "hi" }) {
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState("");
  const cardRef = useRef(null);

  const bName = beneficiary?.name || "लाभार्थी (Beneficiary)";
  const bEdu = beneficiary?.education_level || "10th Pass";
  const bDistrict = beneficiary?.location_district || "Ahmedabad";
  const bState = beneficiary?.location_state || "Gujarat";
  const bSkills = (beneficiary?.existing_skills || []).join(", ") || "General Skills";
  const bInterests = (beneficiary?.interests || []).join(", ") || "Technical Trade";

  const rec = topRecommendation;
  const cardId = `PMAJAY-2026-${bDistrict.substring(0, 3).toUpperCase()}-${Math.floor(100000 + Math.random() * 900000)}`;

  useEffect(() => {
    if (isOpen && rec) {
      const qrPayload = JSON.stringify({
        portal: "PM-AJAY GIA Livelihood Assistant",
        card_id: cardId,
        beneficiary_name: bName,
        district: bDistrict,
        recommended_trade: `${rec.job_role_id} - ${rec.trade_title}`,
        nsqf_level: rec.nsqf_level,
        pm_ajay_grant: rec.self_employment_route?.pm_ajay_grant_support || "₹50,000 GIA Subsidy",
        verification_status: "OFFICIALLY VERIFIED"
      });

      QRCode.toDataURL(qrPayload, {
        width: 140,
        margin: 1,
        color: {
          dark: "#0f172a",
          light: "#ffffff"
        }
      })
        .then((url) => setQrCodeDataUrl(url))
        .catch((err) => console.error("QR Code Error:", err));
    }
  }, [isOpen, rec, bName, bDistrict]);

  if (!isOpen || !rec) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleWhatsAppShare = () => {
    const text = `*PM-AJAY GIA Livelihood & Skilling Recommendation Slip*\n\n` +
      `👤 *Beneficiary:* ${bName}\n` +
      `📍 *District:* ${bDistrict}, ${bState}\n` +
      `🎯 *Recommended Trade:* ${rec.trade_title} (NSQF Level ${rec.nsqf_level})\n` +
      `💰 *PM-AJAY Grant:* ${rec.self_employment_route?.pm_ajay_grant_support || "₹50,000"}\n` +
      `🏢 *Training Center:* ${rec.nearby_training_centers?.[0]?.name || "District Center"}\n` +
      `📞 *Contact:* ${rec.nearby_training_centers?.[0]?.phone || "District Social Welfare Office"}\n\n` +
      `Verified under PM-AJAY GIA Component (Govt. of India)`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
  };

  return (
    <div className="livelihood-modal-backdrop" onClick={onClose}>
      <div className="livelihood-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Action Header Bar (Excluded in print) */}
        <div className="modal-actions-bar no-print">
          <div className="modal-title-left">
            <Sparkles size={18} color="#f97316" />
            <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>
              {language === "gu" ? "પીએમ-અજય સત્તાવાર આજીવિકા કાર્ડ" : language === "hi" ? "पीएम-अजय आधिकारिक आजीविका कार्ड" : "Official PM-AJAY Livelihood Card"}
            </span>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button className="card-action-btn primary" onClick={handlePrint} title="Print or Save PDF">
              <Printer size={15} />
              <span>{language === "gu" ? "પ્રિન્ટ / PDF" : language === "hi" ? "प्रिंट / सेव PDF" : "Print / Save PDF"}</span>
            </button>
            <button className="card-action-btn whatsapp" onClick={handleWhatsAppShare} title="Share on WhatsApp">
              <Share2 size={15} />
              <span>WhatsApp</span>
            </button>
            <button className="card-close-btn" onClick={onClose} title="Close">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Printable Official Government Card */}
        <div className="printable-card" ref={cardRef}>
          {/* Top Indian Tricolor Strip */}
          <div className="card-tricolor-strip">
            <div style={{ background: "#ff9933", height: "4px", flex: 1 }} />
            <div style={{ background: "#ffffff", height: "4px", flex: 1 }} />
            <div style={{ background: "#138808", height: "4px", flex: 1 }} />
          </div>

          {/* Official Emblem & Header */}
          <div className="card-official-header">
            <div className="emblem-seal">
              <div className="lion-circle">
                <ShieldCheck size={26} color="#0f172a" />
              </div>
              <div className="emblem-text">
                <div style={{ fontSize: "0.68rem", fontWeight: 800, letterSpacing: "1px", textTransform: "uppercase", color: "#64748b" }}>
                  Government of India
                </div>
                <div style={{ fontSize: "0.82rem", fontWeight: 800, color: "#0f172a" }}>
                  Ministry of Social Justice and Empowerment
                </div>
                <div style={{ fontSize: "0.72rem", color: "#475569" }}>
                  Department of Social Justice and Empowerment • PM-AJAY (GIA Component)
                </div>
              </div>
            </div>

            <div className="card-id-block">
              <div style={{ fontSize: "0.65rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase" }}>CARD ID / पंजीयन क्रमांक</div>
              <div style={{ fontSize: "0.92rem", fontWeight: 800, color: "#c2410c", fontFamily: "monospace" }}>{cardId}</div>
              <div className="verified-chip">
                <ShieldCheck size={11} />
                <span>NCVET NSQF VERIFIED</span>
              </div>
            </div>
          </div>

          <div className="card-title-banner">
            <span>OFFICIAL NSQF LIVELIHOOD & SKILLING RECOMMENDATION SLIP</span>
            <div style={{ fontSize: "0.75rem", fontWeight: 500, opacity: 0.9 }}>
              (पीएम-अजय विशेष केंद्रीय सहायता घटक अंतर्गत आधिकारिक संस्तुति पत्र)
            </div>
          </div>

          {/* Main Card Body */}
          <div className="card-grid">
            {/* Beneficiary Details Column */}
            <div className="card-section">
              <div className="card-section-title">
                <span>1. BENEFICIARY PROFILE / लाभार्थी विवरण</span>
              </div>
              <div className="card-detail-row">
                <span className="detail-label">Name / नाम:</span>
                <span className="detail-val" style={{ fontWeight: 800, color: "#0f172a" }}>{bName}</span>
              </div>
              <div className="card-detail-row">
                <span className="detail-label">District / जिला:</span>
                <span className="detail-val">{bDistrict}, {bState}</span>
              </div>
              {beneficiary?.full_address && (
                <div className="card-detail-row">
                  <span className="detail-label">Address / पता:</span>
                  <span className="detail-val" style={{ fontSize: "0.76rem" }}>{beneficiary.full_address} {beneficiary.pincode ? `(${beneficiary.pincode})` : ""}</span>
                </div>
              )}
              <div className="card-detail-row">
                <span className="detail-label">Education / योग्यता:</span>
                <span className="detail-val">{bEdu}</span>
              </div>
              <div className="card-detail-row">
                <span className="detail-label">Prior Skills / पूर्व हुनर:</span>
                <span className="detail-val">{bSkills}</span>
              </div>
              <div className="card-detail-row">
                <span className="detail-label">Expressed Interest / रुचि:</span>
                <span className="detail-val">{bInterests}</span>
              </div>
              <div className="card-detail-row">
                <span className="detail-label">Category / श्रेणी:</span>
                <span className="detail-val" style={{ fontWeight: 700, color: "#15803d" }}>Scheduled Caste (SC) - 100% Free GIA</span>
              </div>
            </div>

            {/* Recommended NSQF Trade Column */}
            <div className="card-section highlight">
              <div className="card-section-title">
                <span>2. RECOMMENDED NSQF TRADE / संस्तुत ट्रेड</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                <div>
                  <div style={{ fontSize: "1.05rem", fontWeight: 800, color: "#0f172a" }}>{rec.trade_title}</div>
                  <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "#c2410c" }}>{rec.trade_title_hi || rec.trade_title_gu}</div>
                </div>
                <div className="nsqf-badge-level">
                  <Award size={14} />
                  <span>NSQF Level {rec.nsqf_level}</span>
                </div>
              </div>

              <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
                <span className="card-metric-pill">Code: {rec.job_role_id}</span>
                <span className="card-metric-pill score">Match: {rec.overall_match_score}%</span>
                <span className="card-metric-pill duration">{rec.training_duration_hours} Hrs Free</span>
              </div>

              <div className="pathways-box">
                <div className="pathway-item">
                  <div style={{ fontSize: "0.68rem", fontWeight: 700, color: "#0369a1", textTransform: "uppercase" }}>💼 WAGE EMPLOYMENT PATHWAY</div>
                  <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#0f172a" }}>{rec.wage_route?.job_role || "Technician"}</div>
                  <div style={{ fontSize: "0.72rem", color: "#475569" }}>Salary: {rec.wage_route?.starting_salary_range}</div>
                </div>
                <div className="pathway-item" style={{ borderColor: "#86efac", background: "#f0fdf4" }}>
                  <div style={{ fontSize: "0.68rem", fontWeight: 700, color: "#15803d", textTransform: "uppercase" }}>🏪 PM-AJAY GIA SELF-EMPLOYMENT</div>
                  <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#0f172a" }}>{rec.self_employment_route?.enterprise_name || "Enterprise"}</div>
                  <div style={{ fontSize: "0.72rem", color: "#166534", fontWeight: 600 }}>Grant: {rec.self_employment_route?.pm_ajay_grant_support}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Training Center & Verification QR Footer */}
          <div className="card-bottom-grid">
            <div className="card-section">
              <div className="card-section-title">
                <span>3. ALLOTTED PM-AJAY TRAINING CENTER / प्रशिक्षण केंद्र</span>
              </div>
              {rec.nearby_training_centers && rec.nearby_training_centers[0] ? (
                <div className="center-info-block">
                  <div style={{ fontWeight: 800, color: "#0f172a", fontSize: "0.88rem" }}>
                    {rec.nearby_training_centers[0].name}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.76rem", color: "#475569", marginTop: "3px" }}>
                    <MapPin size={12} />
                    <span>{rec.nearby_training_centers[0].address} ({rec.nearby_training_centers[0].district})</span>
                  </div>
                  <div style={{ display: "flex", gap: "14px", fontSize: "0.76rem", color: "#334155", marginTop: "4px", flexWrap: "wrap" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <Phone size={12} color="#c2410c" />
                      <span>{rec.nearby_training_centers[0].phone}</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <Calendar size={12} color="#15803d" />
                      <span>Next Batch: <strong>{rec.nearby_training_centers[0].next_batch_date || "Immediate"}</strong></span>
                    </div>
                    <div>Stipend: <strong>₹{rec.nearby_training_centers[0].free_daily_stipend_inr}/day</strong></div>
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                  District Social Welfare & Training Office, {bDistrict}
                </div>
              )}
            </div>

            {/* QR Code & Authority Seal */}
            <div className="card-qr-box">
              {qrCodeDataUrl ? (
                <img src={qrCodeDataUrl} alt="Verification QR Code" className="qr-img" />
              ) : (
                <div style={{ width: 100, height: 100, background: "#e2e8f0" }} />
              )}
              <div className="qr-caption">
                <div style={{ fontSize: "0.68rem", fontWeight: 800, color: "#0f172a" }}>SCAN TO VERIFY</div>
                <div style={{ fontSize: "0.62rem", color: "#64748b" }}>MoSJE AI Engine</div>
                <div style={{ fontSize: "0.6rem", color: "#15803d", fontWeight: 700 }}>✓ VALID FOR GIA GRANT</div>
              </div>
            </div>
          </div>

          {/* Footer Declaration */}
          <div className="card-legal-footer">
            <div>
              * Certified under Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY) Grant-in-Aid component. Eligible for 100% free NSQF certification, toolkit, and capital subsidy.
            </div>
            <div style={{ textAlign: "right" }}>
              Issue Date: {new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

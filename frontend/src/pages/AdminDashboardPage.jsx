import React, { useState, useEffect } from "react";
import {
  Users,
  GraduationCap,
  Award,
  Briefcase,
  Store,
  AlertTriangle,
  IndianRupee,
  Search,
  Filter,
  PlusCircle,
  CheckCircle,
  Clock
} from "lucide-react";
import { translations } from "../utils/translations";
import { api } from "../services/api";

export default function AdminDashboardPage({ currentLang }) {
  const t = translations[currentLang] || translations.hi;

  const [kpis, setKpis] = useState(null);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [interventions, setInterventions] = useState([]);
  const [districtFilter, setDistrictFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // Intervention modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState(null);
  const [interventionType, setInterventionType] = useState("PM-AJAY GIA Grant Application");
  const [priority, setPriority] = useState("Medium");
  const [notes, setNotes] = useState("");

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [kpiRes, benRes, intRes] = await Promise.all([
        api.getAdminKPIs(),
        api.listBeneficiaries(districtFilter, statusFilter),
        api.getInterventions(),
      ]);
      setKpis(kpiRes);
      setBeneficiaries(benRes);
      setInterventions(intRes);
    } catch (err) {
      console.error("Failed to load admin data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [districtFilter, statusFilter]);

  const handleOpenInterventionModal = (beneficiary) => {
    setSelectedBeneficiary(beneficiary);
    setNotes("");
    setIsModalOpen(true);
  };

  const handleCreateIntervention = async (e) => {
    e.preventDefault();
    if (!selectedBeneficiary) return;

    try {
      await api.createIntervention({
        beneficiary_id: selectedBeneficiary.id,
        intervention_type: interventionType,
        priority: priority,
        notes: notes,
      });
      setIsModalOpen(false);
      loadData();
    } catch (err) {
      console.error("Failed to create intervention:", err);
    }
  };

  const handleResolveTicket = async (ticketId) => {
    try {
      await api.updateIntervention(ticketId, { status: "Resolved" });
      loadData();
    } catch (err) {
      console.error("Failed to resolve ticket:", err);
    }
  };

  const filteredBeneficiaries = beneficiaries.filter((b) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (b.name && b.name.toLowerCase().includes(q)) ||
      (b.location_district && b.location_district.toLowerCase().includes(q)) ||
      (b.education_level && b.education_level.toLowerCase().includes(q))
    );
  });

  return (
    <div className="admin-dashboard-page">
      <div className="section-heading">
        <h2>{t.adminDashboardTitle}</h2>
        <p>{t.adminSub}</p>
      </div>

      {/* KPI Cards Grid */}
      {kpis && (
        <div className="admin-kpi-grid">
          <div className="kpi-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.totalBeneficiaries}</span>
              <Users size={18} color="#2563eb" />
            </div>
            <div className="kpi-value">{kpis.total_beneficiaries}</div>
            <div className="kpi-sub">100% SC बहुल क्लस्टर</div>
          </div>

          <div className="kpi-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.inTraining}</span>
              <GraduationCap size={18} color="#ea580c" />
            </div>
            <div className="kpi-value">{kpis.in_training}</div>
            <div className="kpi-sub">NSQF स्तर 3 व 4 बैच</div>
          </div>

          <div className="kpi-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.certified}</span>
              <Award size={18} color="#10b981" />
            </div>
            <div className="kpi-value">{kpis.certified}</div>
            <div className="kpi-sub">सरकारी प्रमाण पत्र जारी</div>
          </div>

          <div className="kpi-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.placed}</span>
              <Briefcase size={18} color="#0284c7" />
            </div>
            <div className="kpi-value">{kpis.placed}</div>
            <div className="kpi-sub">{kpis.placement_rate_percent}% प्लेसमेंट दर</div>
          </div>

          <div className="kpi-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.selfEmployed}</span>
              <Store size={18} color="#8b5cf6" />
            </div>
            <div className="kpi-value">{kpis.self_employed}</div>
            <div className="kpi-sub">पीएम-अजय GIA सहायता प्राप्त</div>
          </div>

          <div className="kpi-card">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.interventionsNeeded}</span>
              <AlertTriangle size={18} color="#f43f5e" />
            </div>
            <div className="kpi-value" style={{ color: "#f43f5e" }}>
              {kpis.interventions_needed}
            </div>
            <div className="kpi-sub" style={{ color: "#f43f5e" }}>
              {kpis.open_tickets} सक्रिय फील्ड टिकट
            </div>
          </div>

          <div className="kpi-card" style={{ gridColumn: "span 2" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span className="kpi-title">{t.estimatedGrants}</span>
              <IndianRupee size={18} color="#059669" />
            </div>
            <div className="kpi-value" style={{ color: "#059669" }}>
              ₹{kpis.estimated_grant_disbursed_inr.toLocaleString("en-IN")}
            </div>
            <div className="kpi-sub">निःशुल्क टूलकिट एवं पूंजीगत सब्सिडी बैंक लिंकेज</div>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div style={{
        background: "#ffffff",
        border: "1px solid var(--border-light)",
        borderRadius: "12px",
        padding: "1rem",
        marginBottom: "1.5rem",
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flex: 1, minWidth: "220px" }}>
          <Search size={18} color="#64748b" />
          <input
            id="admin-search-input"
            type="text"
            placeholder="लाभार्थी का नाम, जिला या शिक्षा खोजें..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem 0.75rem",
              border: "1px solid var(--border-light)",
              borderRadius: "8px",
              fontSize: "0.85rem"
            }}
          />
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <select
            id="filter-district-select"
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
            style={{
              padding: "0.5rem 0.75rem",
              borderRadius: "8px",
              border: "1px solid var(--border-light)",
              fontSize: "0.85rem",
              background: "#ffffff"
            }}
          >
            <option value="">सभी जिले (All Districts - 66 Total)</option>
            <optgroup label="📍 गुजरात (33 Districts)">
              <option value="Ahmedabad">अहमदाबाद (Ahmedabad)</option>
              <option value="Amreli">अमरेली (Amreli)</option>
              <option value="Anand">आणंद (Anand)</option>
              <option value="Aravalli">अरावली (Aravalli)</option>
              <option value="Banaskantha">बनासकांठा (Banaskantha)</option>
              <option value="Bharuch">भरूच (Bharuch)</option>
              <option value="Bhavnagar">भावनगर (Bhavnagar)</option>
              <option value="Botad">बोटाद (Botad)</option>
              <option value="Chhota Udaipur">छोटा उदयपुर (Chhota Udaipur)</option>
              <option value="Dahod">दाहोद (Dahod)</option>
              <option value="Dang">डांग (Dang)</option>
              <option value="Devbhumi Dwarka">देवभूमि द्वारका (Devbhumi Dwarka)</option>
              <option value="Gandhinagar">गांधीनगर (Gandhinagar)</option>
              <option value="Gir Somnath">गिर सोमनाथ (Gir Somnath)</option>
              <option value="Jamnagar">जामनगर (Jamnagar)</option>
              <option value="Junagadh">जूनागढ़ (Junagadh)</option>
              <option value="Kheda">खेड़ा (Kheda)</option>
              <option value="Kutch">कच्छ (Kutch)</option>
              <option value="Mahisagar">महिसागर (Mahisagar)</option>
              <option value="Mehsana">मेहसाणा (Mehsana)</option>
              <option value="Morbi">मोरबी (Morbi)</option>
              <option value="Narmada">नर्मदा (Narmada)</option>
              <option value="Navsari">नवसारी (Navsari)</option>
              <option value="Panchmahal">पंचमहल (Panchmahal)</option>
              <option value="Patan">पाटन (Patan)</option>
              <option value="Porbandar">पोरबंदर (Porbandar)</option>
              <option value="Rajkot">राजकोट (Rajkot)</option>
              <option value="Sabarkantha">साबरकांठा (Sabarkantha)</option>
              <option value="Surat">सूरत (Surat)</option>
              <option value="Surendranagar">सुरेंद्रनगर (Surendranagar)</option>
              <option value="Tapi">तापी (Tapi)</option>
              <option value="Vadodara">वडोदरा (Vadodara)</option>
              <option value="Valsad">वलसाड (Valsad)</option>
            </optgroup>
            <optgroup label="📍 राजस्थान (33 Districts)">
              <option value="Ajmer">अजमेर (Ajmer)</option>
              <option value="Alwar">अलवर (Alwar)</option>
              <option value="Banswara">बांसवाड़ा (Banswara)</option>
              <option value="Baran">बारां (Baran)</option>
              <option value="Barmer">बाड़मेर (Barmer)</option>
              <option value="Bharatpur">भरतपुर (Bharatpur)</option>
              <option value="Bhilwara">भीलवाड़ा (Bhilwara)</option>
              <option value="Bikaner">बीकानेर (Bikaner)</option>
              <option value="Bundi">बूंदी (Bundi)</option>
              <option value="Chittorgarh">चित्तौड़गढ़ (Chittorgarh)</option>
              <option value="Churu">चूरू (Churu)</option>
              <option value="Dausa">दौसा (Dausa)</option>
              <option value="Dholpur">धौलपुर (Dholpur)</option>
              <option value="Dungarpur">डूंगरपुर (Dungarpur)</option>
              <option value="Hanumangarh">हनुमानगढ़ (Hanumangarh)</option>
              <option value="Jaipur">जयपुर (Jaipur)</option>
              <option value="Jaisalmer">जैसलमेर (Jaisalmer)</option>
              <option value="Jalore">जालौर (Jalore)</option>
              <option value="Jhalawar">झालावाड़ (Jhalawar)</option>
              <option value="Jhunjhunu">झुंझुनू (Jhunjhunu)</option>
              <option value="Jodhpur">जोधपुर (Jodhpur)</option>
              <option value="Karauli">करौली (Karauli)</option>
              <option value="Kota">कोटा (Kota)</option>
              <option value="Nagaur">नागौर (Nagaur)</option>
              <option value="Pali">पाली (Pali)</option>
              <option value="Pratapgarh">प्रतापगढ़ (Pratapgarh)</option>
              <option value="Rajsamand">राजसमंद (Rajsamand)</option>
              <option value="Sawai Madhopur">सवाई माधोपुर (Sawai Madhopur)</option>
              <option value="Sikar">सीकर (Sikar)</option>
              <option value="Sirohi">सिरोही (Sirohi)</option>
              <option value="Sri Ganganagar">श्रीगंगानगर (Sri Ganganagar)</option>
              <option value="Tonk">टोंक (Tonk)</option>
              <option value="Udaipur">उदयपुर (Udaipur)</option>
            </optgroup>
          </select>

          <select
            id="filter-status-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: "0.5rem 0.75rem",
              borderRadius: "8px",
              border: "1px solid var(--border-light)",
              fontSize: "0.85rem"
            }}
          >
            <option value="">सभी स्थितियां (All Status)</option>
            <option value="Profiled">Profiled</option>
            <option value="In Training">In Training</option>
            <option value="Certified">Certified</option>
            <option value="Placed">Placed</option>
            <option value="Self Employed">Self Employed</option>
            <option value="Intervention Needed">Intervention Needed</option>
          </select>
        </div>
      </div>

      {/* Beneficiary Ledger Table */}
      <div className="admin-data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>लाभार्थी नाम (Beneficiary)</th>
              <th>जिला / ब्लॉक</th>
              <th>शिक्षा स्तर</th>
              <th>विद्यमान कौशल (Skills)</th>
              <th>पसंद (Preference)</th>
              <th>वर्तमान स्थिति</th>
              <th>कार्रवाई</th>
            </tr>
          </thead>
          <tbody>
            {filteredBeneficiaries.map((b) => (
              <tr key={b.id}>
                <td>
                  <strong>{b.name || "अनाम लाभार्थी"}</strong>
                  <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                    {b.phone_number || "फ़ोन उपलब्ध नहीं"} • {b.gender || "M/F"} ({b.age || "25"} वर्ष)
                  </div>
                </td>
                <td>{b.location_district} {b.location_block ? `(${b.location_block})` : ""}</td>
                <td>{b.education_level || "No Formal"}</td>
                <td>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "3px", maxWidth: "200px" }}>
                    {b.existing_skills?.slice(0, 3).map((s, i) => (
                      <span key={i} className="skill-pill matching" style={{ fontSize: "0.68rem" }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </td>
                <td>{b.livelihood_preference}</td>
                <td>
                  <span className={`status-pill ${b.status}`}>
                    {b.status}
                  </span>
                </td>
                <td>
                  <button
                    className="btn-secondary"
                    style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
                    onClick={() => handleOpenInterventionModal(b)}
                  >
                    सहायता टिकट
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Active Ground Intervention Tickets */}
      <div style={{ marginTop: "2rem" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <AlertTriangle size={18} color="#f43f5e" />
          फील्ड सहायता एवं हस्तक्षेप टिकट (Ground Support Queue)
        </h3>
        <div className="admin-data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>लाभार्थी</th>
                <th>हस्तक्षेप का प्रकार</th>
                <th>असाइन फील्ड अधिकारी</th>
                <th>प्राथमिकता</th>
                <th>टिप्पणी / स्थिति</th>
                <th>कार्रवाई</th>
              </tr>
            </thead>
            <tbody>
              {interventions.map((ticket) => (
                <tr key={ticket.id}>
                  <td>
                    <strong>{ticket.beneficiary_name}</strong>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      {ticket.beneficiary_district}
                    </div>
                  </td>
                  <td>{ticket.intervention_type}</td>
                  <td>
                    {ticket.assigned_officer_name}
                    <div style={{ fontSize: "0.72rem", color: "#64748b" }}>
                      {ticket.assigned_officer_phone}
                    </div>
                  </td>
                  <td>
                    <span style={{
                      color: ticket.priority === "High" ? "#e11d48" : "#d97706",
                      fontWeight: 700
                    }}>
                      {ticket.priority}
                    </span>
                  </td>
                  <td>
                    <p style={{ fontSize: "0.8rem", color: "#475569" }}>{ticket.notes}</p>
                    <span className={`status-pill ${ticket.status}`} style={{ marginTop: "4px" }}>
                      {ticket.status}
                    </span>
                  </td>
                  <td>
                    {ticket.status !== "Resolved" ? (
                      <button
                        className="btn-primary"
                        style={{ padding: "0.3rem 0.6rem", fontSize: "0.75rem" }}
                        onClick={() => handleResolveTicket(ticket.id)}
                      >
                        <CheckCircle size={14} /> समाधान मार्क करें
                      </button>
                    ) : (
                      <span style={{ color: "#059669", fontWeight: 600, fontSize: "0.75rem" }}>
                        ✓ समाधानित
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Intervention Modal */}
      {isModalOpen && selectedBeneficiary && (
        <div style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          padding: "1rem"
        }}>
          <div style={{
            background: "#ffffff",
            borderRadius: "16px",
            maxWidth: "500px",
            width: "100%",
            padding: "1.75rem",
            boxShadow: "var(--shadow-lg)"
          }}>
            <h3 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: "0.5rem" }}>
              फील्ड सहायता टिकट जारी करें
            </h3>
            <p style={{ fontSize: "0.85rem", color: "#64748b", marginBottom: "1rem" }}>
              लाभार्थी: <strong>{selectedBeneficiary.name}</strong> ({selectedBeneficiary.location_district})
            </p>

            <form onSubmit={handleCreateIntervention}>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 700, marginBottom: "4px" }}>
                  हस्तक्षेप प्रकार (Intervention Type)
                </label>
                <select
                  value={interventionType}
                  onChange={(e) => setInterventionType(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                >
                  <option value="PM-AJAY GIA Grant Application">पीएम-अजय GIA स्वरोजगार अनुदान सहायता (₹50,000)</option>
                  <option value="Mobilization & Counseling">ड्रॉप-आउट जोखिम / काउंसलिंग सहायता</option>
                  <option value="Mobility Support">दिव्यांगता / परिवहन वाहन व्यवस्था</option>
                  <option value="Artisan Toolkit Delivery">निःशुल्क आधुनिक टूलकिट वितरण</option>
                  <option value="Placement Followup">रोजगार / इंटरव्यू समन्वय</option>
                </select>
              </div>

              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 700, marginBottom: "4px" }}>
                  प्राथमिकता (Priority)
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                >
                  <option value="Medium">सामान्य (Medium)</option>
                  <option value="High">उच्च (High)</option>
                  <option value="Urgent">अति आवश्यक (Urgent)</option>
                </select>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 700, marginBottom: "4px" }}>
                  फील्ड अधिकारी हेतु निर्देश / टिप्पणी (Notes)
                </label>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="लाभार्थी की परिस्थिति, बैंक लिंकेज या प्रशिक्षण केंद्र संबंधी निर्देश लिखें..."
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                  required
                />
              </div>

              <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setIsModalOpen(false)}
                >
                  रद्द करें
                </button>
                <button type="submit" className="btn-primary">
                  टिकट असाइन करें
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

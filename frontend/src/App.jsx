import React, { useState } from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import VoiceAssistantPage from "./pages/VoiceAssistantPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import LowTechDemoPage from "./pages/LowTechDemoPage";

export default function App() {
  const [currentLang, setCurrentLang] = useState("hi");
  const [currentTab, setCurrentTab] = useState("voice");

  return (
    <div className="app-container">
      <Header
        currentLang={currentLang}
        setLang={setCurrentLang}
        currentTab={currentTab}
        setTab={setCurrentTab}
      />

      <main className="main-wrapper">
        {currentTab === "voice" && (
          <VoiceAssistantPage currentLang={currentLang} />
        )}
        {currentTab === "admin" && (
          <AdminDashboardPage currentLang={currentLang} />
        )}
        {currentTab === "lowtech" && (
          <LowTechDemoPage currentLang={currentLang} />
        )}
      </main>

      <Footer />
    </div>
  );
}

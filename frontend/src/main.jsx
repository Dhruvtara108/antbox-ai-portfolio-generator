import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = import.meta.env.DEV ? "http://localhost:8000" : "/api";

function App() {
  const [form, setForm] = useState({ name: "", email: "", phone: "", location: "", role: "" });
  const [files, setFiles] = useState({ resume: null, joining_document: null });
  const [status, setStatus] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [profile, setProfile] = useState(null);
  const [portfolioHtml, setPortfolioHtml] = useState("");

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  function downloadPortfolio() {
    if (!portfolioHtml) {
      setStatus("Generate a portfolio before downloading HTML.");
      return;
    }

    try {
      const candidateName = typeof profile?.name === "string" ? profile.name.trim() : "";
      const safeName = candidateName
        .replace(/[<>:"/\\|?*\u0000-\u001f]/g, "_")
        .replace(/\s+/g, "_")
        .replace(/^\.+|\.+$/g, "")
        .replace(/^_+|_+$/g, "");
      const filename = `${safeName || "Generated_Portfolio"}_Portfolio.html`;
      const blob = new Blob([portfolioHtml], { type: "text/html;charset=utf-8" });
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
    } catch (error) {
      setStatus(error instanceof Error ? `Download failed: ${error.message}` : "Download failed.");
    }
  }

  async function submit(event) {
    event.preventDefault();
    setStatus("");
    setIsSubmitting(true);
    const body = new FormData();
    Object.entries(form).forEach(([key, value]) => body.append(key, value));
    body.append("resume", files.resume);
    body.append("joining_document", files.joining_document);

    try {
      const response = await fetch(`${API_URL}/generate-portfolio`, { method: "POST", body });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Portfolio generation failed.");
      if (typeof result.html !== "string" || !result.html.trim()) {
        throw new Error("The backend returned no rendered portfolio HTML.");
      }
      setProfile(result.profile);
      setPortfolioHtml(result.html);
      setStatus("Portfolio generated successfully.");
    } catch (error) {
      setProfile(null);
      setPortfolioHtml("");
      setStatus(error instanceof Error ? error.message : "Portfolio generation failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="shell">
      <section className="panel">
        <p className="eyebrow">ANTBOX · AI PORTFOLIO GENERATOR</p>
        <h1>Turn candidate evidence into a portfolio.</h1>
        <p className="intro">Upload the resume and joining document. The backend will validate structured candidate data before it reaches the approved portfolio design.</p>
        <form onSubmit={submit}>
          <div className="grid">
            {[
              ["name", "Candidate name", true],
              ["email", "Email", false],
              ["phone", "Phone", false],
              ["location", "Location", false],
              ["role", "Target role", false],
            ].map(([name, label, required]) => (
              <label key={name}>{label}<input name={name} value={form[name]} onChange={updateField} required={required} /></label>
            ))}
          </div>
          <div className="uploads">
            <label>Resume (PDF or DOCX)<input type="file" accept=".pdf,.docx" required onChange={(e) => setFiles({ ...files, resume: e.target.files[0] })} /></label>
            <label>Joining document / job description<input type="file" accept=".pdf,.docx" required onChange={(e) => setFiles({ ...files, joining_document: e.target.files[0] })} /></label>
          </div>
          <button disabled={isSubmitting || !files.resume || !files.joining_document}>{isSubmitting ? "Generating..." : "Generate portfolio"}</button>
          {status && <p className="status" role="status">{status}</p>}
        </form>
      </section>
      <section className="preview">
        <div className="preview-head">
          <p className="eyebrow">PREVIEW</p>
          {portfolioHtml && (
            <button className="download-button" type="button" onClick={downloadPortfolio} disabled={isSubmitting}>
              Download HTML
            </button>
          )}
        </div>
        <iframe
          title="Generated portfolio preview"
          srcDoc={portfolioHtml}
          aria-label={profile ? `Generated portfolio for ${profile.name || "candidate"}` : "Generated portfolio preview"}
        />
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);

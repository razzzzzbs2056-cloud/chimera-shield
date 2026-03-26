"use client";
import { useState } from "react";
import axios from "axios";

type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

interface ScanResult {
  risk_score: number;
  risk_level: RiskLevel;
  is_phishing: boolean;
  indicators: string[];
  recommendation: string;
}

const riskColors: Record<RiskLevel, string> = {
  LOW: "text-green-400 border-green-400",
  MEDIUM: "text-yellow-400 border-yellow-400",
  HIGH: "text-orange-400 border-orange-400",
  CRITICAL: "text-red-400 border-red-400",
};

const riskBg: Record<RiskLevel, string> = {
  LOW: "bg-green-900/20",
  MEDIUM: "bg-yellow-900/20",
  HIGH: "bg-orange-900/20",
  CRITICAL: "bg-red-900/20",
};

export default function ScanPage() {
  const [sender, setSender] = useState("");
  const [subject, setSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleScan = async () => {
    if (!emailBody.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await axios.post("http://localhost:8000/api/scan/email", {
        email_content: emailBody,
        sender,
        subject,
      });
      setResult(data);
    } catch {
      setError("Scan failed. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <span className="text-xs font-semibold text-blue-400 tracking-widest uppercase">
            ChimeraShield
          </span>
          <h1 className="text-3xl font-bold mt-1">AI Phishing Detector</h1>
          <p className="text-gray-400 mt-1">
            Paste any suspicious email below. Our AI will analyze it instantly.
          </p>
        </div>

        <div className="space-y-3">
          <input
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
            placeholder="Sender email (optional)"
            value={sender}
            onChange={(e) => setSender(e.target.value)}
          />
          <input
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
            placeholder="Subject line (optional)"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
          <textarea
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-blue-500 resize-none"
            placeholder="Paste email body here..."
            rows={8}
            value={emailBody}
            onChange={(e) => setEmailBody(e.target.value)}
          />
        </div>

        <button
          onClick={handleScan}
          disabled={loading || !emailBody.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-semibold transition"
        >
          {loading ? "Analyzing..." : "Scan Email"}
        </button>

        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className={`border rounded-lg p-6 space-y-4 ${riskBg[result.risk_level]} border-gray-700`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-widest">Risk Level</p>
                <p className={`text-2xl font-bold mt-1 ${riskColors[result.risk_level]}`}>
                  {result.risk_level}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400 uppercase tracking-widest">Risk Score</p>
                <p className={`text-4xl font-bold mt-1 ${riskColors[result.risk_level]}`}>
                  {result.risk_score}
                  <span className="text-lg text-gray-500">/100</span>
                </p>
              </div>
            </div>

            <div className="border-t border-gray-700 pt-4">
              <p className="text-xs text-gray-400 uppercase tracking-widest mb-2">Red Flags Detected</p>
              {result.indicators.length === 0 ? (
                <p className="text-sm text-gray-400">No suspicious indicators found.</p>
              ) : (
                <ul className="space-y-1">
                  {result.indicators.map((indicator, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <span className="text-red-400 mt-0.5">•</span>
                      <span>{indicator}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="border-t border-gray-700 pt-4">
              <p className="text-xs text-gray-400 uppercase tracking-widest mb-2">Recommendation</p>
              <p className="text-sm font-medium">{result.recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

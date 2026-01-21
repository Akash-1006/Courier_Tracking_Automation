import React, { useState } from "react";
import { postFormData } from "../api";

/* ---------- Flag Badge Component ---------- */
const FlagBadge = ({ flag }) => {
  const colors = {
    DUPLICATE_STATEMENT: "#ffe066",
    DUPLICATE_RECEIPT: "#74c0fc",
    COLLISION: "#ff6b6b",
  };

  return (
    <span
      style={{
        background: colors[flag] || "#ddd",
        padding: "4px 8px",
        marginRight: 6,
        borderRadius: 6,
        fontSize: 12,
        fontWeight: "bold",
      }}
    >
      {flag}
    </span>
  );
};

export default function ReceiptReconcil() {
  const [statement, setStatement] = useState(null);
  const [receipts, setReceipts] = useState([]);
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("matched");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const submit = async () => {
    setErrorMsg("");
    if (!statement || receipts.length === 0) {
      setErrorMsg("Please upload statement and receipt PDFs");
      return;
    }

    const formData = new FormData();
    formData.append("statement", statement);
    receipts.forEach((r) => formData.append("receipts", r));

    setLoading(true);
    try {
      const data = await postFormData("/reconcile", formData);
      setResult(data);
      setTab("matched");
    } catch (err) {
      setErrorMsg(err?.message || "Error during reconciliation");
    } finally {
      setLoading(false);
    }
  };

  const activeTabClass =
    "bg-gradient-to-r from-accent to-primary-blue text-white";
  const inactiveTabClass = "bg-slate-800 hover:bg-slate-700/70";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Receipt Reconcil</h1>

      <div className="bg-card-bg p-4 md:p-6 rounded-xl shadow-xl space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-l bold mb-2">
              <b>Bank Statement PDF</b>
            </label>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setStatement(e.target.files?.[0] || null)}
              className="block text-text-muted"
              disabled={loading}
            />
          </div>

          <div>
          <label className="block text-l bold mb-2">
              <b>Receipt PDFs</b>
            </label>
            <input
              type="file"
              accept="application/pdf"
              multiple
              onChange={(e) => setReceipts([...(e.target.files || [])])}
              className="block text-text-muted"
              disabled={loading}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={submit}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              loading
                ? "bg-slate-600 cursor-not-allowed"
                : "bg-accent hover:bg-primary-blue text-white"
            }`}
          >
            {loading ? "Processing..." : "Reconcile"}
          </button>

          {errorMsg && <p className="text-red-400 font-semibold">{errorMsg}</p>}
        </div>
      </div>

      {result && (
        <div className="bg-card-bg p-6 rounded-xl shadow-xl">
          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={() => setTab("matched")}
              className={`px-3 py-2 rounded-lg font-semibold transition ${
                tab === "matched" ? activeTabClass : inactiveTabClass
              }`}
            >
              ✔ Matched ({result.matched_count})
            </button>
            <button
              onClick={() => setTab("missed")}
              className={`px-3 py-2 rounded-lg font-semibold transition ${
                tab === "missed" ? activeTabClass : inactiveTabClass
              }`}
            >
              ❌ Missed ({result.missed_count})
            </button>
          </div>

          {tab === "matched" && (
            <>
              <h2 className="text-lg font-bold mb-3">✔ Matched Entries</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-700">
                  <thead className="bg-slate-700/40">
                    <tr>
                      <th className="px-3 py-2 text-left">Stmt Date</th>
                      <th className="px-3 py-2 text-left">Description</th>
                      <th className="px-3 py-2 text-left">Amount</th>
                      <th className="px-3 py-2 text-center">↔</th>
                      <th className="px-3 py-2 text-left">Receipt Date</th>
                      <th className="px-3 py-2 text-left">Receipt Amount</th>
                      <th className="px-3 py-2 text-left">Flags</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {(result.matched || []).map((m, i) => (
                      <tr key={i} className="hover:bg-slate-700/30">
                        <td className="px-3 py-2">{m.statement?.date}</td>
                        <td className="px-3 py-2">
                          {m.statement?.description}
                        </td>
                        <td className="px-3 py-2">{m.statement?.amount}</td>
                        <td className="px-3 py-2 text-center">✔</td>
                        <td className="px-3 py-2">{m.receipt?.date}</td>
                        <td className="px-3 py-2">{m.receipt?.amount}</td>
                        <td className="px-3 py-2">
                          {(m.flags || []).length > 0 ? (
                            m.flags.map((f, idx) => (
                              <FlagBadge key={idx} flag={f} />
                            ))
                          ) : (
                            <span>-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {tab === "missed" && (
            <>
              <h2 className="text-lg font-bold mb-3">❌ Missed Entries</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-700">
                  <thead className="bg-slate-700/40">
                    <tr>
                      <th className="px-3 py-2 text-left">Date</th>
                      <th className="px-3 py-2 text-left">Description</th>
                      <th className="px-3 py-2 text-left">Amount</th>
                      <th className="px-3 py-2 text-left">Flags</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {(result.missed || []).map((e, i) => (
                      <tr key={i} className="hover:bg-slate-700/30">
                        <td className="px-3 py-2">{e.date}</td>
                        <td className="px-3 py-2">{e.description}</td>
                        <td className="px-3 py-2">{e.amount}</td>
                        <td className="px-3 py-2">
                          {(e.flags || []).length > 0 ? (
                            e.flags.map((f, idx) => (
                              <FlagBadge key={idx} flag={f} />
                            ))
                          ) : (
                            <span>-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}



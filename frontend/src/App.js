import { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";

// -----------------------------------------------------
// ✅ MAIN APP LAYOUT
// -----------------------------------------------------
export default function App() {
  return (
    <Router>
      <div className="min-h-screen flex bg-dark-bg text-text-light">
        
        {/* Sidebar */}
        <nav className="w-50 bg-sidebar-bg p-6 flex flex-col shadow-xl">
          <h2 className="text-xl font-bold mb-10">Courier Dashboard</h2>

          <ul className="space-y-4">
            <li>
              <Link to="/" className="block p-3 rounded-lg hover:bg-slate-700/50">
                Tracking Table
              </Link>
            </li>
            <li>
              <Link to="/upload" className="block p-3 rounded-lg hover:bg-slate-700/50">
                Upload Excel
              </Link>
            </li>
          </ul>
        </nav>

        <main className="flex-1 p-10">
          <Routes>
            <Route path="/" element={<TrackPage />} />
            <Route path="/upload" element={<UploadPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}



// -----------------------------------------------------
// ✅ TRACKING PAGE
// -----------------------------------------------------
function TrackPage() {

  // ✅ Convert yyyy-mm-dd → dd-mm-yyyy
  function formatTDate(date) {
    if (!date) return "—";
    const [y, m, d] = date.split("-");
    return `${d}-${m}-${y}`;
  }

  // ✅ Round weight
  function roundWeight(w) {
    if (!w) return "—";
    const num = parseFloat(w);
    if (isNaN(num)) return w;
    return Math.round(num);
  }

  // ✅ Convert UTC timestamp → dd-mm-yyyy hh:mm:ss
  function formatTimestamp(ts) {
    if (!ts) return "—";

    const dt = new Date(ts);
    const d = String(dt.getDate()).padStart(2, "0");
    const m = String(dt.getMonth() + 1).padStart(2, "0");
    const y = dt.getFullYear();

    const hh = String(dt.getHours()).padStart(2, "0");
    const mm = String(dt.getMinutes()).padStart(2, "0");
    const ss = String(dt.getSeconds()).padStart(2, "0");

    return `${d}-${m}-${y} ${hh}:${mm}:${ss}`;
  }

  const [data, setData] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [modal, setModal] = useState(null);
  const [trackingAll, setTrackingAll] = useState(false);

  const loadData = async () => {
    const res = await fetch("http://127.0.0.1:5000/consignments");
    const d = await res.json();

    const cleaned = d.map(item => ({
      ...item,
      tdate: item.tdate ? item.tdate.split(" ")[0] : null
    }));

    // ✅ Sort: Pending first → then by TDate DESC
    const sorted = cleaned.sort((a, b) => {
      // Step 1: Pending first
      if (a.delivered !== b.delivered) {
        return a.delivered ? 1 : -1;  // delivered goes below
      }

      // Step 2: Sort by newest date
      const da = new Date(a.tdate);
      const db = new Date(b.tdate);
      return db - da;
    });

    setData(sorted);
  };

  useEffect(() => {
    loadData();
  }, []);

  const trackAll = async () => {
    setTrackingAll(true);
    await fetch("http://127.0.0.1:5000/track_consignments");
    await loadData();
    setTrackingAll(false);
  };

  // ✅ Filter + Search (CNo + Cnee)
  const filteredData = data.filter(row => {
    const q = search.toLowerCase();
    const match =
      row.cno.toLowerCase().includes(q) ||
      (row.cnee && row.cnee.toLowerCase().includes(q));

    if (filter === "delivered") return row.delivered && match;
    if (filter === "pending") return !row.delivered && match;
    return match;
  });

  return (
    <>
      {/* Header */}
      <div className="flex justify-between mb-3">
        <div className="flex items-center gap-1 mb-1">
      <img 
       src="/fledge_logo.png" 
         alt="Logo" 
           className="w-20 h-20 object-contain"
          />
         <h2 className="text-2xl font-bold">Fledge Enterprises</h2>
        </div>

        <button
          onClick={trackAll}
          disabled={trackingAll}
          className={`mt-5 mb-5 px-2 py-1 rounded-lg ${
            trackingAll ? "bg-slate-600" : "bg-accent hover:bg-primary-blue"
          }`}
        >
          {trackingAll ? "Updating..." : "Track All"}
        </button>
      </div>

      {/* Search + Filter */}
      <div className="flex items-center justify-between mb-4">
        <input
          type="text"
          placeholder="Search..."
          className="px-3 py-2 bg-slate-800 rounded-lg w-64"
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="px-3 py-2 bg-slate-800 rounded-lg"
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All</option>
          <option value="delivered">Delivered</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-card-bg p-6 rounded-xl shadow-xl overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-700">
          <thead>
            <tr className="bg-slate-700/40">
              <th className="px-4 py-3 text-left">CNo</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">T-Date</th>
              <th className="px-4 py-3 text-left">Cnee</th>
              <th className="px-4 py-3 text-left">Destination</th>
              <th className="px-4 py-3 text-left">Pincode</th>
              <th className="px-4 py-3 text-left">Weight</th>
              <th className="px-4 py-3 text-left">Pcs</th>
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {filteredData.map((item, index) => (
              <>
                <tr
                  key={index}
                  className="hover:bg-slate-700/30 cursor-pointer"
                  onClick={() => setExpanded(expanded === index ? null : index)}
                >
                  <td className="px-4 py-3">{item.cno}</td>

                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded text-sm ${
                        item.delivered
                          ? "bg-green-700 text-green-300"
                          : "bg-blue-700 text-blue-300"
                      }`}
                    >
                      {item.delivered ? "Delivered" : "In Transit"}
                    </span>
                  </td>

                  <td className="px-4 py-3">{formatTDate(item.tdate)}</td>
                  <td className="px-4 py-3">{item.cnee || "—"}</td>
                  <td className="px-4 py-3">{item.destn}</td>
                  <td className="px-4 py-3">{item.cpincode}</td>
                  <td className="px-4 py-3">{roundWeight(item.wt)}</td>
                  <td className="px-4 py-3">{item.pcs}</td>

                  <td className="px-4 py-3">
                    <button
                      className="px-3 py-1 bg-accent rounded-lg hover:bg-primary-blue"
                      onClick={(e) => {
                        e.stopPropagation();
                        setModal(item);
                      }}
                    >
                      View History
                    </button>
                  </td>
                </tr>

                {expanded === index && (
                  <tr className="bg-slate-800/40">
                    <td colSpan="9" className="p-4 space-y-2">
                      <p><strong>Full Status:</strong> {item.status}</p>
                      <p>Date: {formatTDate(item.tdate)}</p>
                      <p>Cnee: {item.cnee || "—"}</p>
                      <p>Last Checked: {formatTimestamp(item.last_checked)}</p>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {modal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-10">
          <div className="bg-sidebar-bg p-8 rounded-xl w-96 relative">
            <button
              className="absolute top-3 right-3 text-xl"
              onClick={() => setModal(null)}
            >
              ✖
            </button>

            <h2 className="text-xl font-bold mb-4">{modal.cno} - Details</h2>

            <p>Status: {modal.status}</p>
            <p>T-Date: {formatTDate(modal.tdate)}</p>
            <p>Cnee: {modal.cnee}</p>
            <p>Destination: {modal.destn}</p>
            <p>Pincode: {modal.cpincode}</p>
            <p>Weight: {roundWeight(modal.wt)}</p>
            <p>Pcs: {modal.pcs}</p>
            <p>Last Checked: {formatTimestamp(modal.last_checked)}</p>

          </div>
        </div>
      )}
    </>
  );
}




// -----------------------------------------------------
// ✅ UPLOAD PAGE
// -----------------------------------------------------
function UploadPage() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false); // ✅ NEW

  const upload = async () => {
    if (!file) return;

    setLoading(true);  // ✅ Show loading

    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: fd,
      });

      const d = await res.json();
      setMsg(`${d.message} (${d.count})`);
    } catch (err) {
      setMsg("Upload failed.");
    }

    setLoading(false); // ✅ Hide loading
  };

  return (
    <>
      <h1 className="text-3xl font-semibold mb-6 text-accent">Upload Excel</h1>

      <div className="bg-card-bg p-8 rounded-xl shadow-xl relative">

        {/* ✅ Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center rounded-xl">
            <div className="h-10 w-10 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-3 text-lg text-accent font-semibold">Uploading...</p>
          </div>
        )}

        <input
          type="file"
          accept=".xls,.xlsx"
          className="mb-4 block text-text-muted"
          onChange={(e) => setFile(e.target.files[0])}
          disabled={loading}   // ✅ disable while uploading
        />

        <button
          className={`px-6 py-2 rounded-lg font-semibold ${
            loading
              ? "bg-slate-600 cursor-not-allowed"
              : "bg-accent hover:bg-primary-blue"
          }`}
          onClick={upload}
          disabled={loading}   // ✅ prevent double upload
        >
          {loading ? "Uploading..." : "Upload"}
        </button>

        {msg && <p className="mt-4 text-green-400">{msg}</p>}
      </div>
    </>
  );
}


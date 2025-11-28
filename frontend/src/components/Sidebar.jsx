import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="w-50 bg-sidebar-bg p-6 flex flex-col shadow-xl">
      <h2 className="text-xl font-bold mb-10">Courier Dashboard</h2>

      <ul className="space-y-3">
        {/* Professional Courier */}
        <li className="text-text-muted uppercase tracking-wide text-sm">
          Professional Courier
        </li>
        <li className="ml-4">
          <Link
            to="/"
            className={`block p-2 rounded-lg ${
              isActive("/")
                ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                : "hover:bg-slate-700/50"
            }`}
          >
            Tracking Table
          </Link>
        </li>
        <li className="ml-4">
          <Link
            to="/upload"
            className={`block p-2 rounded-lg ${
              isActive("/upload")
                ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                : "hover:bg-slate-700/50"
            }`}
          >
            Upload Excel
          </Link>
        </li>

        {/* Divider */}
        <hr className="border-slate-700 my-2" />

        {/* Franch Express */}
        <li className="text-text-muted uppercase tracking-wide text-sm">
          Franch Express
        </li>
        <li className="ml-4">
          <Link
            to="/fe_consignments"
            className={`block p-2 rounded-lg ${
              isActive("/fe_consignments")
                ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                : "hover:bg-slate-700/50"
            }`}
          >
            Tracking Table
          </Link>
        </li>
        <li className="ml-4">
          <Link
            to="/upload_fe"
            className={`block p-2 rounded-lg ${
              isActive("/upload_fe")
                ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                : "hover:bg-slate-700/50"
            }`}
          >
            Upload Excel
          </Link>
        </li>
      </ul>
    </nav>
  );
}

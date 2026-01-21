import { useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;
  const isInSection = (paths) => paths.some((p) => location.pathname === p);

  const [open, setOpen] = useState({
    courier: true,
    assistant: false,
  });

  const courierPaths = useMemo(
    () => ["/", "/upload", "/fe_consignments", "/upload_fe"],
    []
  );
  const assistantPaths = useMemo(
    () => ["/assistant/receipt-reconcil", "/assistant/invoice-assist"],
    []
  );

  return (
    <nav className="w-full md:w-64 lg:w-72 bg-sidebar-bg p-4 md:p-6 flex flex-col shadow-xl">
      <div className="flex items-center gap-3 mb-4 md:mb-6">
        <img
          src="/fledge_logo.png"
          alt="Fledge Logo"
          className="w-10 h-10 object-contain"
        />
        <h2 className="text-xl font-bold">Fledge Utils</h2>
      </div>
      

      <ul className="space-y-3">
        {/* Courier Dashboard (collapsible) */}
        <li>
          <button
            type="button"
            onClick={() => setOpen((o) => ({ ...o, courier: !o.courier }))}
            className={`w-full flex items-center justify-between p-2 rounded-lg font-semibold transition ${
              isInSection(courierPaths)
                ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                : "hover:bg-slate-700/50"
            }`}
          >
            <span>Courier Dashboard</span>
            <span className="text-sm">{open.courier ? "▾" : "▸"}</span>
          </button>

          {open.courier && (
            <ul className="mt-3 space-y-3">
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
          )}
        </li>

        {/* Divider */}
        <hr className="border-slate-700 my-2" />

        {/* Assistant (collapsible) */}
        <li>
          <button
            type="button"
            onClick={() => setOpen((o) => ({ ...o, assistant: !o.assistant }))}
            className={`w-full flex items-center justify-between p-2 rounded-lg font-semibold transition ${
              isInSection(assistantPaths)
                ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                : "hover:bg-slate-700/50"
            }`}
          >
            <span>Assistant</span>
            <span className="text-sm">{open.assistant ? "▾" : "▸"}</span>
          </button>

          {open.assistant && (
            <ul className="mt-3 space-y-3">
              <li className="ml-4">
                <Link
                  to="/assistant/invoice-assist"
                  className={`block p-2 rounded-lg ${
                    isActive("/assistant/invoice-assist")
                      ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                      : "hover:bg-slate-700/50"
                  }`}
                >
                  Invoice Assist
                </Link>
              </li>
              <li className="ml-4">
                <Link
                  to="/assistant/receipt-reconcil"
                  className={`block p-2 rounded-lg ${
                    isActive("/assistant/receipt-reconcil")
                      ? "bg-gradient-to-r from-accent to-primary-blue text-white"
                      : "hover:bg-slate-700/50"
                  }`}
                >
                  Receipt Reconcil
                </Link>
              </li>
              
            </ul>
          )}
        </li>
      </ul>
    </nav>
  );
}

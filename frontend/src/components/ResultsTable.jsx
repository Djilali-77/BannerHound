import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowDown,
  ArrowUp,
  Download,
  Globe,
  Monitor,
  Router,
  Search,
  Server,
} from "lucide-react";
import RiskBadge from "./RiskBadge";
import { downloadReport } from "../lib/api";
import { RISK_LEVELS, RISK_RANK } from "../lib/risk";

const SERVICE_NAMES = { 22: "SSH", 23: "Telnet", 80: "HTTP", 443: "HTTPS" };

function getDeviceIcon(type) {
  const text = type.toLowerCase();
  if (text.includes("router") || text.includes("switch")) return Router;
  if (text.includes("web")) return Globe;
  if (
    text.includes("server") ||
    text.includes("linux") ||
    text.includes("raspberry") ||
    text.includes("embedded")
  ) {
    return Server;
  }
  return Monitor;
}

// "192.168.1.10" -> number, so IPs are sorted numerically and not as text
function ipToNumber(ip) {
  return ip.split(".").reduce((total, part) => total * 256 + Number(part), 0);
}

const SORTERS = {
  IP: (a, b) => ipToNumber(a.IP) - ipToNumber(b.IP),
  "Device Type": (a, b) => a["Device Type"].localeCompare(b["Device Type"]),
  Risk: (a, b) =>
    (RISK_RANK[a.Risk] ?? 9) - (RISK_RANK[b.Risk] ?? 9) ||
    ipToNumber(a.IP) - ipToNumber(b.IP),
};

function SortHeader({ label, sortKey, sort, onSort }) {
  const active = sort.key === sortKey;
  const Arrow = sort.dir === "asc" ? ArrowUp : ArrowDown;
  const ariaSort = active ? (sort.dir === "asc" ? "ascending" : "descending") : "none";

  return (
    <th className="p-4 border-b border-bronze/20" aria-sort={ariaSort}>
      <button
        type="button"
        onClick={() => onSort(sortKey)}
        className="inline-flex items-center gap-1 uppercase hover:text-white transition-colors"
      >
        {label}
        {active && <Arrow size={14} />}
      </button>
    </th>
  );
}

export default function ResultsTable({ results, scanId, canExport }) {
  const [query, setQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState("All");
  const [sort, setSort] = useState({ key: "IP", dir: "asc" });
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  const riskCounts = useMemo(() => {
    const counts = { All: results.length };
    RISK_LEVELS.forEach((level) => {
      counts[level] = results.filter((row) => row.Risk === level).length;
    });
    return counts;
  }, [results]);

  const rows = useMemo(() => {
    const search = query.trim().toLowerCase();

    const filtered = results.filter((device) => {
      if (riskFilter !== "All" && device.Risk !== riskFilter) return false;
      if (!search) return true;
      return [device.IP, device["Device Type"], device.Banner].some((value) =>
        String(value).toLowerCase().includes(search)
      );
    });

    const sorter = SORTERS[sort.key];
    const direction = sort.dir === "asc" ? 1 : -1;
    return [...filtered].sort((a, b) => sorter(a, b) * direction);
  }, [results, query, riskFilter, sort]);

  if (results.length === 0) return null;

  const handleSort = (key) => {
    setSort((current) =>
      current.key === key
        ? { key, dir: current.dir === "asc" ? "desc" : "asc" }
        : { key, dir: "asc" }
    );
  };

  const handleExport = async () => {
    setExporting(true);
    setExportError("");
    try {
      await downloadReport(scanId);
    } catch (err) {
      setExportError(err.message || "Failed to download the report.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto mb-8">
      {/* Toolbar: search, risk filter and export */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div className="relative md:w-72">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
          />
          <input
            type="text"
            aria-label="Search results"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search IP, device or banner"
            className="w-full bg-navy-dark border border-gray-700 text-white pl-9 pr-3 py-2 rounded-xl text-sm focus:outline-none focus:border-bronze transition-colors"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {["All", ...RISK_LEVELS].map((level) => (
            <button
              key={level}
              type="button"
              onClick={() => setRiskFilter(level)}
              className={`px-3 py-1 rounded-full border text-sm transition-colors ${
                riskFilter === level
                  ? "border-bronze bg-bronze/10 text-bronze"
                  : "border-gray-700 text-gray-400 hover:border-bronze/50"
              }`}
            >
              {level} ({riskCounts[level]})
            </button>
          ))}
        </div>

        <motion.button
          type="button"
          whileHover={{ scale: canExport ? 1.05 : 1 }}
          whileTap={{ scale: canExport ? 0.95 : 1 }}
          onClick={handleExport}
          disabled={!canExport || exporting}
          title={canExport ? "Download the CSV report" : "Available when the scan is finished"}
          className="bg-navy-dark border border-bronze/50 hover:bg-bronze hover:text-white text-bronze px-4 py-2 rounded-xl font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-40 disabled:hover:bg-navy-dark disabled:hover:text-bronze"
        >
          <Download size={18} />
          <span>{exporting ? "Exporting..." : "Export CSV"}</span>
        </motion.button>
      </div>

      {exportError && (
        <p role="alert" className="text-sm text-red-400 mb-4 text-right">
          {exportError}
        </p>
      )}

      <div className="overflow-hidden rounded-2xl border border-bronze/20 shadow-2xl bg-navy">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-navy-dark text-bronze uppercase text-sm">
                <SortHeader label="IP Address" sortKey="IP" sort={sort} onSort={handleSort} />
                <SortHeader
                  label="Device Type"
                  sortKey="Device Type"
                  sort={sort}
                  onSort={handleSort}
                />
                <th className="p-4 border-b border-bronze/20">Open Ports</th>
                <SortHeader label="Risk" sortKey="Risk" sort={sort} onSort={handleSort} />
                <th className="p-4 border-b border-bronze/20">Service Banner</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((device) => {
                const DeviceIcon = getDeviceIcon(device["Device Type"]);
                const ports = device["Open Ports"] || [];

                return (
                  <motion.tr
                    key={device.IP}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.25 }}
                    className="hover:bg-navy-dark/50 transition-colors border-b border-gray-800 last:border-0"
                  >
                    <td className="p-4 font-mono text-gray-300 whitespace-nowrap">
                      {device.IP}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <DeviceIcon className="text-bronze shrink-0" size={20} />
                        <span>{device["Device Type"]}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1">
                        {ports.map((port) => (
                          <span
                            key={port}
                            className="px-2 py-0.5 rounded-md bg-navy-dark border border-gray-700 text-xs font-mono text-gray-300"
                          >
                            {port}
                            {SERVICE_NAMES[port] ? ` ${SERVICE_NAMES[port]}` : ""}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="p-4">
                      <RiskBadge risk={device.Risk} reason={device["Risk Reason"]} />
                      <p className="mt-1 text-xs text-gray-500 max-w-[16rem]">
                        {device["Risk Reason"]}
                      </p>
                    </td>
                    <td
                      className="p-4 font-mono text-sm text-gray-400 truncate max-w-xs"
                      title={device.Banner}
                    >
                      {device.Banner}
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {rows.length === 0 && (
          <p className="p-6 text-center text-gray-500">No hosts match your filters.</p>
        )}
      </div>
    </div>
  );
}
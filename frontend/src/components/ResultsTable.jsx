import { motion } from "framer-motion";
import { Monitor, Router, ShieldAlert, Download } from "lucide-react";

export default function ResultsTable({ results }) {
  if (!results || results.length === 0) return null;

  const getIcon = (type) => {
    if (type.includes("Router") || type.includes("Switch")) return <Router className="text-bronze" size={20} />;
    if (type.includes("Server") || type.includes("Linux")) return <Monitor className="text-blue-400" size={20} />;
    return <ShieldAlert className="text-gray-400" size={20} />;
  };

  const handleDownloadCSV = async () => {
    try {
        const response = await fetch("http://localhost:8000/api/download-report");
        if (!response.ok) {
            alert("Report not found! Please run a scan first.");
            return;
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "network_audit_report.csv");
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Error downloading the CSV:", error);
        alert("Failed to download the report.");
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto mb-8">
      
      <div className="flex justify-end mb-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleDownloadCSV}
          className="bg-navy-dark border border-bronze/50 hover:bg-bronze hover:text-white text-bronze px-4 py-2 rounded-xl font-medium flex items-center gap-2 transition-colors"
        >
          <Download size={18} />
          <span>Export CSV</span>
        </motion.button>
      </div>

      <div className="overflow-hidden rounded-2xl border border-bronze/20 shadow-2xl bg-navy">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-navy-dark text-bronze uppercase text-sm">
                <th className="p-4 border-b border-bronze/20">IP Address</th>
                <th className="p-4 border-b border-bronze/20">Status</th>
                <th className="p-4 border-b border-bronze/20">Device Type</th>
                <th className="p-4 border-b border-bronze/20">Service Banner</th>
              </tr>
            </thead>
            <tbody>
              {results.map((device, index) => (
                <motion.tr
                  key={device.IP}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="hover:bg-navy-dark/50 transition-colors border-b border-gray-800 last:border-0"
                >
                  <td className="p-4 font-mono text-gray-300">{device.IP}</td>
                  <td className="p-4">
                    <span className="bg-green-500/10 text-green-400 px-3 py-1 rounded-full text-sm font-medium border border-green-500/20">
                      {device.Status}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      {getIcon(device['Device Type'])}
                      <span>{device['Device Type']}</span>
                    </div>
                  </td>
                  <td className="p-4 font-mono text-sm text-gray-400 truncate max-w-xs" title={device.Banner}>
                    {device.Banner}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
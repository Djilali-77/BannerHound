// Base URL of the backend. Falls back to the local default.
export const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

/** Build the URL of the CSV report of a scan (or the latest one). */
export function reportUrl(scanId) {
  const base = `${API_URL}/api/download-report`;
  return scanId ? `${base}?scan_id=${encodeURIComponent(scanId)}` : base;
}

/** Download the CSV report of a scan as a file. */
export async function downloadReport(scanId) {
  const response = await fetch(reportUrl(scanId));
  if (!response.ok) {
    throw new Error("Report not found. Please run a scan first.");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "network_audit_report.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();

  URL.revokeObjectURL(url);
}
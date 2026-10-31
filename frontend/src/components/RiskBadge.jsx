import { getRiskStyle } from "../lib/risk";

export default function RiskBadge({ risk, reason }) {
  const { icon: Icon, badge } = getRiskStyle(risk);

  return (
    <span
      title={reason}
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${badge}`}
    >
      <Icon size={14} />
      {risk}
    </span>
  );
}
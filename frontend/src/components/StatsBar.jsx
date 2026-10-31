import { useMemo } from "react";

export default function StatsBar({ results }) {
  const stats = useMemo(() => {
    const count = (levels) => results.filter((row) => levels.includes(row.Risk)).length;

    return [
      { label: "Hosts found", value: results.length, color: "text-white" },
      { label: "High risk", value: count(["High"]), color: "text-red-400" },
      { label: "Medium risk", value: count(["Medium"]), color: "text-orange-400" },
      { label: "Low / Info", value: count(["Low", "Info"]), color: "text-green-400" },
    ];
  }, [results]);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-5xl mx-auto mb-6">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="bg-navy border border-bronze/20 rounded-2xl p-4 text-center"
        >
          <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
          <div className="text-sm text-gray-400 mt-1">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
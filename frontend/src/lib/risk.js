import { ShieldAlert, Shield, ShieldCheck, Info } from "lucide-react";

export const RISK_LEVELS = ["High", "Medium", "Low", "Info"];

// Lower number = more dangerous (used when sorting by risk)
export const RISK_RANK = { High: 0, Medium: 1, Low: 2, Info: 3 };

// Full class names are written out so Tailwind can detect them
export const RISK_STYLES = {
  High: {
    icon: ShieldAlert,
    badge: "bg-red-500/10 text-red-400 border-red-500/30",
  },
  Medium: {
    icon: Shield,
    badge: "bg-orange-500/10 text-orange-400 border-orange-500/30",
  },
  Low: {
    icon: ShieldCheck,
    badge: "bg-green-500/10 text-green-400 border-green-500/30",
  },
  Info: {
    icon: Info,
    badge: "bg-gray-500/10 text-gray-400 border-gray-500/30",
  },
};

export function getRiskStyle(risk) {
  return RISK_STYLES[risk] || RISK_STYLES.Info;
}
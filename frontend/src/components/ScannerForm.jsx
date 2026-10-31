import { motion } from "framer-motion";
import { Search, Square } from "lucide-react";

const PRESETS = [
  { label: "Lab network", value: "172.28.0.0/24" },
  { label: "Demo data", value: "test" },
  { label: "Home network", value: "192.168.1.0/24" },
];

export default function ScannerForm({ subnet, setSubnet, onScan, onStop, scanning }) {
  const handleSubmit = (event) => {
    event.preventDefault();
    if (!scanning) onScan();
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-navy p-6 rounded-2xl shadow-lg border border-bronze/20 w-full max-w-2xl mx-auto mb-8"
    >
      <div className="flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          aria-label="Target subnet"
          value={subnet}
          onChange={(event) => setSubnet(event.target.value)}
          placeholder="Example: 192.168.1.0/24"
          className="flex-1 bg-navy-dark border border-gray-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:border-bronze transition-colors disabled:opacity-50"
          disabled={scanning}
        />

        {scanning ? (
          <motion.button
            type="button"
            onClick={onStop}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-red-500/10 border border-red-500/50 text-red-400 hover:bg-red-500 hover:text-white px-8 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors"
          >
            <Square size={18} />
            <span>Stop</span>
          </motion.button>
        ) : (
          <motion.button
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-bronze hover:bg-[#b87029] text-white px-8 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors"
          >
            <Search size={20} />
            <span>Scan</span>
          </motion.button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2 mt-4 text-sm">
        <span className="text-gray-500">Quick targets:</span>
        {PRESETS.map((preset) => (
          <button
            key={preset.value}
            type="button"
            disabled={scanning}
            onClick={() => setSubnet(preset.value)}
            className="px-3 py-1 rounded-full border border-gray-700 text-gray-400 hover:border-bronze hover:text-bronze transition-colors disabled:opacity-50"
          >
            {preset.label}
          </button>
        ))}
      </div>
    </motion.form>
  );
}
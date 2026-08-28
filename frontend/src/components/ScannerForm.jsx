import { motion } from "framer-motion";
import { Search } from "lucide-react";

export default function ScannerForm({ subnet, setSubnet, onScan, loading }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-navy p-6 rounded-2xl shadow-lg border border-bronze/20 w-full max-w-2xl mx-auto mb-8"
    >
      <div className="flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          value={subnet}
          onChange={(e) => setSubnet(e.target.value)}
          placeholder="Example: 192.168.1.0/24"
          className="flex-1 bg-navy-dark border border-gray-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:border-bronze transition-colors"
          disabled={loading}
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onScan}
          disabled={loading}
          className="bg-bronze hover:bg-[#b87029] text-white px-8 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
        >
          {loading ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
            />
          ) : (
            <>
              <Search size={20} />
              <span>Scan</span>
            </>
          )}
        </motion.button>
      </div>
    </motion.div>
  );
}
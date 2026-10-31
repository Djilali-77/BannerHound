import { motion } from "framer-motion";
import { Network } from "lucide-react";

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -30 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center mb-12"
    >
      <div className="flex justify-center mb-4">
        <div className="bg-navy p-4 rounded-full border-2 border-bronze">
          <Network size={40} className="text-bronze" />
        </div>
      </div>
      <h1 className="text-4xl md:text-5xl font-bold mb-4">
        Banner<span className="text-bronze">Hound</span>
      </h1>
      <p className="text-gray-400 max-w-xl mx-auto">
        Credential-less network scanner and OS fingerprinter. Discover live
        devices, identify them from their service banners and spot risky
        services, without logging in to anything.
      </p>
    </motion.header>
  );
}
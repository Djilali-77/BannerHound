import { motion } from "framer-motion";

export default function ScanStatus({ status, found, total, error }) {
  if (status === "idle") return null;

  if (status === "error") {
    return (
      <div
        role="alert"
        className="max-w-2xl mx-auto mb-8 bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-center"
      >
        {error}
      </div>
    );
  }

  if (status === "scanning") {
    // total is null until the API has finished discovering live hosts
    const discovering = total === null;
    const percent = discovering || total === 0 ? 0 : Math.round((found / total) * 100);

    return (
      <div role="status" className="max-w-2xl mx-auto mb-8">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>{discovering ? "Discovering live hosts..." : "Fingerprinting hosts..."}</span>
          {!discovering && (
            <span>
              {found} / {total}
            </span>
          )}
        </div>

        <div className="h-2 bg-navy-dark rounded-full overflow-hidden">
          {discovering ? (
            <motion.div
              className="h-full w-1/3 bg-bronze rounded-full"
              animate={{ x: ["-100%", "300%"] }}
              transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
            />
          ) : (
            <motion.div
              className="h-full bg-bronze rounded-full"
              animate={{ width: `${percent}%` }}
              transition={{ duration: 0.3 }}
            />
          )}
        </div>
      </div>
    );
  }

  const message =
    status === "done"
      ? found === 0
        ? "Scan finished: no live hosts found on this subnet."
        : `Scan finished: ${found} host${found > 1 ? "s" : ""} found.`
      : "Scan stopped. Showing partial results.";

  return (
    <p role="status" className="text-center text-sm text-gray-400 mb-8">
      {message}
    </p>
  );
}
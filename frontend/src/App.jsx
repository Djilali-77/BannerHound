import { useState } from "react";
import Header from "./components/Header";
import ScannerForm from "./components/ScannerForm";
import ScanStatus from "./components/ScanStatus";
import StatsBar from "./components/StatsBar";
import ResultsTable from "./components/ResultsTable";
import Footer from "./components/Footer";
import { useScan } from "./hooks/useScan";

// Default target: the fake network started by docker-compose.lab.yml
const DEFAULT_SUBNET = "172.28.0.0/24";

function App() {
  const [subnet, setSubnet] = useState(DEFAULT_SUBNET);
  const { results, status, error, total, scanId, start, stop } = useScan();

  const scanning = status === "scanning";

  const handleScan = () => {
    if (subnet.trim()) start(subnet);
  };

  return (
    <div className="min-h-screen flex flex-col p-6 md:p-12 selection:bg-bronze selection:text-white">
      <main className="flex-1">
        <Header />

        <ScannerForm
          subnet={subnet}
          setSubnet={setSubnet}
          onScan={handleScan}
          onStop={stop}
          scanning={scanning}
        />

        <ScanStatus status={status} found={results.length} total={total} error={error} />

        {results.length > 0 && <StatsBar results={results} />}

        <ResultsTable results={results} scanId={scanId} canExport={status === "done"} />

        {status === "idle" && (
          <p className="text-center text-gray-500 mt-12">
            Enter a target subnet and click Scan to begin.
          </p>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
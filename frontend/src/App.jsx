import { useState } from 'react'
import axios from 'axios'
import { motion } from 'framer-motion'
import { Network } from 'lucide-react'
import ScannerForm from './components/ScannerForm'
import ResultsTable from './components/ResultsTable'

function App() {
  const [subnet, setSubnet] = useState('192.168.1.0/24')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [error, setError] = useState('')

  const handleScan = async () => {
    if (!subnet) return;
    
    setLoading(true)
    setError('')
    setResults([])

    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/scan`, {
        params: { subnet }
      });
      
      if (response.data.status === "success") {
        setResults(response.data.results)
      }
    } catch (err) {
      setError('Connection failed. Please ensure the FastAPI backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-6 md:p-12 selection:bg-bronze selection:text-white">
      {/* Header */}
      <motion.div 
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
          Network <span className="text-bronze">Scanner</span>
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto">
          Network & OS Fingerprinting Tool. Discover active devices on your network and identify their systems without credentials.
        </p>
      </motion.div>

      {/* Search Form */}
      <ScannerForm 
        subnet={subnet} 
        setSubnet={setSubnet} 
        onScan={handleScan} 
        loading={loading} 
      />

      {/* Error Message */}
      {error && (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          className="max-w-2xl mx-auto mb-8 bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-center"
        >
          {error}
        </motion.div>
      )}

      {/* Empty State Message */}
      {!loading && results.length === 0 && !error && (
         <div className="text-center text-gray-500 mt-12">
            Enter a target subnet and click Scan to begin.
         </div>
      )}

      {/* Results Table */}
      <ResultsTable results={results} />
      
    </div>
  )
}

export default App
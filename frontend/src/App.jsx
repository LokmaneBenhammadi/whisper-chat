import { useEffect, useState } from "react";

function App() {
  const [backendData, setBackendData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Note the trailing slash: "/api/status/"
    // This matches the standard Django URL pattern
    const baseUrl = import.meta.env.VITE_API_URL || "";
    fetch(`${baseUrl}/api/status/`,{
          headers: { "X-Requested-With": "ReactApp" }}
      ).then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP Error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        setBackendData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl text-white font-bold mb-8">
        Frontend &lt;--&gt; Backend Connection
      </h1>

      {/* Card Container */}
      <div className="bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700 w-full max-w-md">
        
        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center space-x-2 text-blue-400">
            <div className="w-4 h-4 rounded-full animate-bounce bg-blue-400"></div>
            <p>Contacting Server...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center">
            <p className="text-red-400 font-bold text-xl mb-2">Connection Failed</p>
            <p className="text-slate-400 text-sm">{error}</p>
          </div>
        )}

        {/* Success State */}
        {backendData && (
          <div className="space-y-4">
            
            {/* Status Indicator */}
            <div className="flex items-center justify-between border-b border-slate-700 pb-4">
              <span className="text-slate-400">System Status:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-bold flex items-center gap-2 ${
                backendData.status === "online" 
                  ? "bg-green-900 text-green-300" 
                  : "bg-red-900 text-red-300"
              }`}>
                {/* The Green Dot */}
                <span className={`w-2 h-2 rounded-full ${
                  backendData.status === "online" ? "bg-green-400" : "bg-red-400"
                }`}></span>
                {backendData.status.toUpperCase()}
              </span>
            </div>

            {/* Message from Django */}
            <div>
              <p className="text-slate-400 text-sm mb-1">Message:</p>
              <p className="text-white text-lg font-medium">"{backendData.message}"</p>
            </div>

            {/* Version */}
            <div className="pt-4 text-right">
              <span className="text-xs text-slate-500 font-mono">
                API v{backendData.version}
              </span>
            </div>
            
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
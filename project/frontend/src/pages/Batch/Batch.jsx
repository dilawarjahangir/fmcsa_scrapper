import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Modal from "../../components/Modal";
import CarrierData from "../../components/CarrierData";

const Batch = () => {
  // Sidebar dates
  const [runDates, setRunDates]         = useState([]);
  const [datesLoading, setDatesLoading] = useState(false);
  const [datesError, setDatesError]     = useState("");
  const navigate = useNavigate();

  // Original batch search state
  const [mcNumber, setMcNumber]     = useState("");
  const [tillNumber, setTillNumber] = useState("");
  const [batchData, setBatchData]   = useState(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");
  const [isOpen, setIsOpen]         = useState(false);
  const [singleData, setSingleData] = useState(null);

  // Fetch run‑dates once
  useEffect(() => {
    setDatesLoading(true);
    fetch("http://localhost:8000/api/carriers/dates")
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(dates => {
        setRunDates(dates);
        setDatesLoading(false);
      })
      .catch(err => {
        console.error(err);
        setDatesError("Failed to load run dates");
        setDatesLoading(false);
      });
  }, []);

  const fetchBatchData = async () => {
    setLoading(true);
    setError("");
    setBatchData(null);

    try {
      const res = await fetch("http://localhost:8000/api/carrier/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mc_number: mcNumber.trim(),
          till_number: Number(tillNumber),
        }),
      });
      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const { results } = await res.json();

      // filter successful
      const filtered = Object.fromEntries(
        Object.entries(results)
          .filter(([, p]) => !p.error && p.data)
          .map(([mc, p]) => [mc, p.data])
      );
      setBatchData(filtered);
      localStorage.setItem("batchData", JSON.stringify(filtered));
      localStorage.setItem("batchSearch", JSON.stringify({ mcNumber, tillNumber }));
    } catch (err) {
      setError(err.message || "Failed to fetch data.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (mcNumber.trim() && tillNumber.trim()) fetchBatchData();
  };

  const renderSummary = (mc, data) => {
    const usdotStatus = data["USDOT INFORMATION"]?.["USDOT Status:"] ?? "";
    const entityType  = data["USDOT INFORMATION"]?.["Entity Type:"]  ?? "";
    return (
      <div
        key={mc}
        className="p-4 bg-white border border-gray-200 rounded shadow cursor-pointer hover:shadow-lg transition"
        onClick={() => { setIsOpen(true); setSingleData(data); }}
      >
        <h2 className="text-xl font-bold mb-2">MC: {mc}</h2>
        <p><span className="font-medium">USDOT Status:</span> {usdotStatus}</p>
        <p><span className="font-medium">Entity Type:</span> {entityType}</p>
      </div>
    );
  };

  return (
    <div className="flex min-h-screen bg-gray-100 font-inter">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r p-6">
        <h2 className="text-xl font-bold mb-4 font-alegreya">Run Dates</h2>
        {datesLoading && <p>Loading dates…</p>}
        {datesError   && <p className="text-red-600">{datesError}</p>}
        <ul className="space-y-2">
          {runDates.map(date => (
            <li key={date}>
              <button
                className="text-blue-600 hover:underline"
                onClick={() => navigate(`/by-date/${date}`)}
              >
                {date}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6">
        <h1 className="text-3xl font-bold mb-6 font-alegreya">
          Batch Carrier Information Lookup
        </h1>

        {/* search form */}
        <form onSubmit={handleSubmit} className="flex flex-col space-y-4 max-w-md">
          <input
            type="text"
            placeholder="Starting MC Number"
            value={mcNumber}
            onChange={e => setMcNumber(e.target.value)}
            className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="number"
            placeholder="Till Number (count)"
            value={tillNumber}
            onChange={e => setTillNumber(e.target.value)}
            className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="w-full px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Search Batch
          </button>
        </form>

        {loading && <p className="mt-4 text-blue-600">Loading…</p>}
        {error   && <p className="mt-4 text-red-600">{error}</p>}

        {batchData && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.keys(batchData).map(mc => renderSummary(mc, batchData[mc]))}
          </div>
        )}

        <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} data={singleData} />
      </main>
    </div>
  );
};

export default Batch;

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CarrierData from '../../components/CarrierData';

const SingleDetail = () => {
  const { mcNumber } = useParams();
  const [carrierData, setCarrierData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCarrierData = async () => {
      setLoading(true);
      setError("");
      setCarrierData(null);
      try {
        const response = await fetch("http://127.0.0.1:8000/api/carrier", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ mc_number: mcNumber })
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const result = await response.json();
        setCarrierData(result.data);
      } catch (err) {
        setError("Failed to fetch data. Please try again.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchCarrierData();
  }, [mcNumber]);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-8 font-inter">
      <h1 className="text-3xl font-bold mb-6 font-alegreya">Carrier Information Detail for MC: {mcNumber}</h1>
      {loading && <p className="mt-4 text-blue-600">Loading...</p>}
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {carrierData && <CarrierData data={carrierData} />}
    </div>
  );
};

export default SingleDetail;

              import React, { useState, useEffect } from "react";
              import { useNavigate } from "react-router-dom";
              import Modal from "../../components/Modal";

              const Batch = () => {
                const [mcNumber, setMcNumber] = useState("");
                const [tillNumber, setTillNumber] = useState("");
                const [batchData, setBatchData] = useState(null);
                const [loading, setLoading] = useState(false);
                const [error, setError] = useState("");
                const [isOpen, setIsOpen] = useState(false);
                const [singleData, setSingleData] = useState(false);

                // const navigate = useNavigate();

                // Load previously searched batch data from localStorage on mount.
                useEffect(() => {
                  const storedData = localStorage.getItem("batchData");
                  const storedParams = localStorage.getItem("batchSearch");
                  if (storedData && storedParams) {
                    setBatchData(JSON.parse(storedData));
                    const { mcNumber, tillNumber } = JSON.parse(storedParams);
                    setMcNumber(mcNumber);
                    setTillNumber(tillNumber);
                  }
                }, []);


                const fetchBatchData = async () => {
                  setLoading(true);
                  setError("");
                  setBatchData({}); // Reset batchData to an empty object
                
                  try {
                    let currentMcNumber = Number(mcNumber); // Ensure it's a number
                
                    for (let i = 0; i < Number(tillNumber); i++) {
                      try {
                        const response = await fetch("http://127.0.0.1:8000/api/carrier", {
                          method: "POST",
                          headers: {
                            "Content-Type": "application/json",
                          },
                          body: JSON.stringify({ mc_number: String(currentMcNumber) }),
                        });
                
                        // Check if the response is not OK (like 500)
                        if (!response.ok) {
                          // Try to extract error details if available
                          let errorMessage = "Server error";
                          try {
                            const errorResult = await response.json();
                            errorMessage = errorResult.error || errorMessage;
                          } catch (jsonError) {
                            // If parsing fails, keep the default error message
                          }
                
                          // Update state with error info for the current MC number
                          setBatchData((prevData) => {
                            const updatedData = {
                              ...prevData,
                              [currentMcNumber]: { error: errorMessage },
                            };
                            localStorage.setItem("batchData", JSON.stringify(updatedData));
                            return updatedData;
                          });
                        } else {
                          const result = await response.json();
                          // Update state with fetched data for the current MC number
                          setBatchData((prevData) => {
                            const updatedData = {
                              ...prevData,
                              [currentMcNumber]: result.data,
                            };
                            localStorage.setItem("batchData", JSON.stringify(updatedData));
                            return updatedData;
                          });
                        }
                      } catch (err) {
                        // Catch network or unexpected errors for the current iteration
                        setBatchData((prevData) => {
                          const updatedData = {
                            ...prevData,
                            [currentMcNumber]: { error: err.message },
                          };
                          localStorage.setItem("batchData", JSON.stringify(updatedData));
                          return updatedData;
                        });
                      }
                      // Move to the next MC number regardless of success or error
                      currentMcNumber++;
                    }
                
                    localStorage.setItem("batchSearch", JSON.stringify({ mcNumber, tillNumber }));
                  } catch (err) {
                    setError("Failed to fetch batch data. Please try again.");
                    console.error(err);
                  } finally {
                    setLoading(false);
                  }
                };
                
                const handleSubmit = (e) => {
                  e.preventDefault();
                  if (mcNumber.trim() && tillNumber.trim()) {
                    fetchBatchData();
                  }
                };

                // Render a summary card for each MC.
                // Only display if the returned data object is non-empty.
                const renderSummary = (mc, data) => {
                  // Skip rendering if the data object is empty
                  if (!data || Object.keys(data).length === 0) return null;

                  if (data.error) {
                    return (
                      <div
                        key={mc}
                        className=" bg-white border border-gray-200 rounded shadow cursor-pointer"
                        // onClick={() => navigate(`/single/${mc}`)}
                        // onClick={() => setIsOpen(true)}
                      >
                        <h2 className="text-xl font-bold mb-2">MC: {mc}</h2>
                        <p className="text-red-500">Error: {data.error}</p>
                      </div>
                    );
                  }
                  // Extract the needed details from the USDOT INFORMATION section.
                  let usdotStatus = "";
                  let entityType = "";
                  if (data["USDOT INFORMATION"]) {
                    usdotStatus =
                      data["USDOT INFORMATION"]["USDOT Status:"] ||
                      data["USDOT INFORMATION"]["USDOT Status"] ||
                      "";
                    entityType =
                      data["USDOT INFORMATION"]["Entity Type:"] ||
                      data["USDOT INFORMATION"]["Entity Type"] ||
                      "";
                  }
                  return (
                    <div
                      key={mc}
                      className="p-4 bg-white border border-gray-200 rounded shadow cursor-pointer hover:shadow-lg transition"
                      // onClick={() => navigate(`/single/${mc}`)}
                      onClick={() => {
                        setIsOpen(true);
                        setSingleData(data);
                      }}
                    >
                      <h2 className="text-xl font-bold mb-2">MC: {mc}</h2>
                      <p>
                        <span className="font-medium">USDOT Status:</span> {usdotStatus}
                      </p>
                      <p>
                        <span className="font-medium">Entity Type:</span> {entityType}
                      </p>
                    </div>
                  );
                };

                return (
                  <div className="min-h-screen bg-gray-100 flex flex-col items-center font-inter">
                    <h1 className="text-3xl font-bold mb-6 font-alegreya">
                      Batch Carrier Information Lookup
                    </h1>
                    <form
                      onSubmit={handleSubmit}
                      className="flex flex-col items-center space-y-4 w-full max-w-md"
                    >
                      <input
                        type="text"
                        placeholder="Starting MC Number"
                        value={mcNumber}
                        onChange={(e) => setMcNumber(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="number"
                        placeholder="Till Number (count)"
                        value={tillNumber}
                        onChange={(e) => setTillNumber(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        type="submit"
                        className="w-full px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                      >
                        Search Batch
                      </button>
                    </form>
                    {loading && <p className="mt-4 text-blue-600">Loading...</p>}
                    {error && <p className="mt-4 text-red-600">{error}</p>}
                    {batchData && (
                      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl">
                        {Object.keys(batchData)
                          .map((mc) => renderSummary(mc, batchData[mc]))
                          .filter((element) => element !== null)}
                      </div>
                    )}
                    <Modal
                      isOpen={isOpen}
                      onClose={() => setIsOpen(false)}
                      data={singleData}
                    />
                  </div>
                );
              };

              export default Batch;

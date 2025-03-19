// src/components/MCInput.js
import React, { useState } from 'react';

const MCInput = ({ onSubmit }) => {
  const [mcNumber, setMcNumber] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (mcNumber.trim() !== "") {
      onSubmit(mcNumber);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-center space-y-4 w-full max-w-md">
      <input
        type="text"
        placeholder="MC Number"
        value={mcNumber}
        onChange={(e) => setMcNumber(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-inter"
      />
      <button
        type="submit"
        className="w-full px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-inter"
      >
        Search
      </button>
    </form>
  );
};

export default MCInput;

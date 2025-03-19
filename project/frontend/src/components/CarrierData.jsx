// src/components/CarrierData.js
import React from 'react';

const CarrierData = ({ data }) => {
  if (!data) {
    return null;
  }

  return (
    <div className="mt-8 space-y-6 w-full max-w-4xl">
      {Object.keys(data).map((sectionKey, idx) => {
        const section = data[sectionKey];
        return (
          <div key={idx} className="p-4 bg-white border border-gray-200 rounded shadow hover:shadow-lg transition">
            <h2 className="text-xl font-bold mb-2 font-alegreya">{sectionKey}</h2>
            <div className="space-y-1">
              {Object.keys(section).map((itemKey, j) => (
                <div key={j} className="flex justify-between border-b border-gray-100 pb-1 font-inter">
                  <span className="font-medium">{itemKey}</span>
                  <span>{section[itemKey]}</span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CarrierData;

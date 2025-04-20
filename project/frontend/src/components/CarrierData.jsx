import React from 'react';

const CarrierData = ({ data }) => {
  if (!data) return null;

  return (
    <div className="mt-8 space-y-6 w-full max-w-4xl">
      {Object.entries(data).map(([sectionKey, section], idx) => (
        <div key={idx} className="p-4 bg-white border rounded shadow">
          <h2 className="text-xl font-bold mb-2">{sectionKey}</h2>
          <div className="space-y-1">
            {Object.entries(section).map(([itemKey, val], j) => (
              <div key={j} className="flex justify-between border-b pb-1">
                <span className="font-medium">{itemKey}</span>
                <span>{val}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default CarrierData;

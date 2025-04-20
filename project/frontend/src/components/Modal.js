import React from 'react';

const overlay = {
  position: 'fixed',
  top: 0, left: 0,
  width: '100vw', height: '100vh',
  background: 'rgba(0,0,0,0.7)',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  zIndex: 1000,
};
const content = {
  width: '60vw',
  maxHeight: '90vh',
  background: 'rgba(0,0,0,0.4)',
  borderRadius: '10px',
  padding: '10px',
  color: 'white',
  boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
  display: 'flex', flexDirection: 'column',
};

export default function Modal({ isOpen, onClose, data, mcNumber, onAction }) {
  if (!isOpen) return null;
  const handle = (action) => onAction(action, mcNumber);

  return (
    <div style={overlay} onClick={onClose}>
      <div style={content} onClick={(e) => e.stopPropagation()}>
        <div className="flex-1 overflow-y-auto">
          {data && Object.entries(data).map(([sec, section], i) => (
            <div key={i} className="p-4 mb-2 bg-white border rounded shadow">
              <h2 className="text-xl font-bold mb-2 text-black">{sec}</h2>
              <div className="space-y-1">
                {Object.entries(section).map(([k, v], j) => (
                  <div key={j} className="flex justify-between border-b pb-1">
                    <span className="font-medium text-black">{k}</span>
                    <span className="text-black">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex justify-between">
          <button
            className={`px-6 py-3 rounded font-semibold transition
              ${data?.called
                ? 'bg-green-700 text-white shadow-lg ring-4 ring-green-300'
                : 'bg-green-600 text-white hover:bg-green-700'}`}
            onClick={() => handle('called')}
          >
            Called
          </button>
          <button
            className={`px-6 py-3 rounded font-semibold transition
              ${data?.lead
                ? 'bg-blue-700 text-white shadow-lg ring-4 ring-blue-300'
                : 'bg-blue-600 text-white hover:bg-blue-700'}`}
            onClick={() => handle('lead')}
          >
            Lead
          </button>
        </div>
      </div>
    </div>
  );
}

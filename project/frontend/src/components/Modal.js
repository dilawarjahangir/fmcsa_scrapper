import React from 'react';

const modalOverlay = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  background: 'rgba(0, 0, 0, 0.7)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
};

const modalContent = {
  width: '60vw',
  height: '90vh',
  background: 'rgba(0, 0, 0, 0.4)',
  borderRadius: '10px',
  padding: '10px',
  color: 'white',
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
  overflowY: 'auto',
};

const Modal = ({ isOpen, onClose, data }) => {
  if (!isOpen) return null;
  console.log(data);

  return (
    <div style={modalOverlay} onClick={onClose}>
      <div style={modalContent} onClick={(e) => e.stopPropagation()}>
        {Object.keys(data).map((sectionKey, idx) => {
          const section = data[sectionKey];
          return (
            <div key={idx} className="p-4 mb-2 bg-white border border-gray-200 rounded shadow hover:shadow-lg transition">
              <h2 className="text-xl font-bold mb-2 text-black font-alegreya">{sectionKey}</h2>
              <div className="space-y-1">
                {Object.keys(section).map((itemKey, j) => (
                  <div key={j} className="flex justify-between border-b border-gray-100 pb-1 font-inter">
                    <span className="font-medium text-black">{itemKey}</span> {/* Black text */}
                    <span className="text-black">{section[itemKey]}</span> {/* Black text */}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Modal;

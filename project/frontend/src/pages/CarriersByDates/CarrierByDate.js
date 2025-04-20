import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Modal from '../../components/Modal';

export default function CarriersByDate() {
  const { date } = useParams();
  const navigate = useNavigate();

  const [carriers, setCarriers] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');
  const [isOpen, setIsOpen]     = useState(false);
  const [modalData, setModalData] = useState(null);
  const [modalMc, setModalMc]     = useState('');

  useEffect(() => {
    fetch(`http://localhost:8000/api/carriers/by-date?date=${date}`)
      .then(r => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then(data => {
        setCarriers(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to load carriers');
        setLoading(false);
      });
  }, [date]);

  const openModal = (data, mc) => {
    setModalData(data);
    setModalMc(mc);
    setIsOpen(true);
  };

  const handleAction = async (action, mc) => {
    try {
      if (action === 'called') {
        // toggle called
        const carrier = carriers.find(c => c.mc_number === mc);
        const nextCalled = !carrier.called;
        const res = await fetch(
          `http://localhost:8000/api/carriers/${mc}/called`,
          {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ called: nextCalled }),
          }
        );
        if (!res.ok) throw new Error(await res.text());
        const updated = await res.json();
        setCarriers(cs =>
          cs.map(c =>
            c.mc_number === mc ? { ...c, called: updated.called } : c
          )
        );

      } else {
        // toggle lead
        const carrier = carriers.find(c => c.mc_number === mc);
        const nextLead = !carrier.lead;
        const res = await fetch(
          `http://localhost:8000/api/carriers/${mc}/lead`,
          {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead: nextLead }),
          }
        );
        if (!res.ok) throw new Error(await res.text());
        const updated = await res.json();
        setCarriers(cs =>
          cs.map(c =>
            c.mc_number === mc ? { ...c, lead: updated.lead } : c
          )
        );
      }
    } catch (err) {
      console.error('Action failed', err);
      setError('Something went wrong; see console.');
    } finally {
      setIsOpen(false);
    }
  };

  if (loading) return <p>Loading…</p>;
  if (error)   return <p className="text-red-600">{error}</p>;

  return (
    <div className="flex min-h-screen bg-gray-100 font-inter">
      <aside className="w-64 bg-white border-r p-6">
        <button
          onClick={() => navigate(-1)}
          className="text-blue-600 hover:underline mb-4"
        >
          ← Back
        </button>
        <h2 className="font-bold mb-2">Date: {date}</h2>
        <p className="text-sm text-gray-600">
          Dot: gray=none, green=called, blue=lead
        </p>
      </aside>

      <main className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-4">Carriers on {date}</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {carriers.map(c => (
            <div
              key={c.mc_number}
              className="p-4 bg-white border rounded shadow cursor-pointer hover:shadow-lg transition"
              onClick={() => openModal(c.data, c.mc_number)}
            >
              <div className="flex items-center mb-2">
                <span
                  className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    c.lead
                      ? 'bg-blue-500'
                      : c.called
                      ? 'bg-green-500'
                      : 'bg-gray-400'
                  }`}
                />
                <h2 className="text-xl font-bold">MC: {c.mc_number}</h2>
              </div>
              <p>
                <span className="font-medium">USDOT Status:</span>{' '}
                {c.data['USDOT INFORMATION']?.['USDOT Status:'] || '—'}
              </p>
              <p>
                <span className="font-medium">Entity Type:</span>{' '}
                {c.data['USDOT INFORMATION']?.['Entity Type:'] || '—'}
              </p>
            </div>
          ))}
        </div>

        <Modal
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          data={modalData}
          mcNumber={modalMc}
          onAction={handleAction}
        />
      </main>
    </div>
  );
}

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Batch from './pages/Batch/Batch';
import SingleDetail from './pages/SingleDetail/SingleDetail';
import CarriersByDate from './pages/CarriersByDates/CarrierByDate';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Batch />} />
        <Route path="/batch" element={<Batch />} />
        <Route path="/single/:mcNumber" element={<SingleDetail />} />
        <Route path="/by-date/:date" element={<CarriersByDate />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </Router>
  );
}

export default App;

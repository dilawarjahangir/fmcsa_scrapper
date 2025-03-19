import { BrowserRouter as Router, Routes,Route } from 'react-router-dom';
import './App.css';
import { ToastContainer } from 'react-toastify';
import Batch from './pages/Batch/Batch';
import SingleDetail from './pages/SingleDetail/SingleDetail';

function App() {
  return (
    <div className="  w-screen h-screen  ">
    
    <Router>
      <Routes>
      <Route path="/" element={<Batch />} />        
        <Route path="/batch" element={<Batch />} />
        <Route path="/single/:mcNumber" element={<SingleDetail />} />
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
    </div>
  );
}

export default App;

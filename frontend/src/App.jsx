import { Route, Routes } from 'react-router-dom';

import ShowsPage from './pages/ShowsPage.jsx';
import ShowDetail from './pages/ShowDetail.jsx';
import TicketsPage from './pages/TicketsPage.jsx';
import './App.css';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ShowsPage />} />
      <Route path="/shows/:id" element={<ShowDetail />} />
      <Route path="/tickets" element={<TicketsPage />} />
    </Routes>
  );
}

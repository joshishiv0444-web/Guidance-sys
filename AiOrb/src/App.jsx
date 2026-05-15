import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import DashboardLayout from './layouts/DashboardLayout';
import UXHeatmaps from './pages/UXHeatmaps';
import AppComplexity from './pages/AppComplexity';
import B2BMarketplace from './pages/B2BMarketplace';
import KnowledgeBase from './pages/KnowledgeBase';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route index element={<Navigate to="heatmaps" replace />} />
        <Route path="heatmaps" element={<UXHeatmaps />} />
        <Route path="complexity" element={<AppComplexity />} />
        <Route path="b2b" element={<B2BMarketplace />} />
        <Route path="knowledge" element={<KnowledgeBase />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

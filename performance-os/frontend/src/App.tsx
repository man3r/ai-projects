import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Goals } from './pages/Goals';
import { FeedbackPage } from './pages/Feedback';
import { Layout } from './components/Layout';
import { Reviews } from './pages/Reviews';

// Placeholder empty pages
const Settings = () => <div className="p-8"><h1 className="text-3xl font-bold">Settings</h1><p className="text-slate-400 mt-2">System configuration and organization management. Coming soon.</p></div>;

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="goals" element={<Goals />} />
            <Route path="reviews" element={<Reviews />} />
            <Route path="feedback" element={<FeedbackPage />} />
            <Route path="settings" element={<Settings />} />
          </Route>

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

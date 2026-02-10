import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import LandingPage from './pages/LandingPage';
import ConsolePage from './pages/ConsolePage';
import CallLogsPage from './pages/CallLogsPage';
import RecordingsPage from './pages/RecordingsPage';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LandingPage />} />

                {/* Protected Dashboard Routes */}
                <Route path="/console" element={<DashboardLayout />}>
                    <Route index element={<ConsolePage />} />
                    <Route path="transcripts" element={<CallLogsPage />} />
                    <Route path="recordings" element={<RecordingsPage />} />
                </Route>

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "../features/dashboard/pages/DashboardPage";
import History from "../features/history/pages/HistoryPage";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/history" element={<History />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
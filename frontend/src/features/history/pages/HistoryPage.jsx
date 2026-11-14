import Header from "../../../shared/layout/Header";
import HistoryFilters from "../components/HistoryFilters";
import HistorySessions from "../components/HistorySessions";
import { useHistoryData } from "../hooks/useHistoryData";
import "../history.css";

function HistoryPage() {
    const data = useHistoryData();

    return (
        <>
            <Header />
            <main className="history-page">
                <h1 className="history-title">History</h1>

                {data.catalogError && (
                    <p className="history-error" role="alert">
                        {data.catalogError}
                    </p>
                )}
                {data.historyError &&
                    data.historyError !== data.catalogError && (
                        <p className="history-error" role="alert">
                            {data.historyError}
                        </p>
                    )}

                <HistoryFilters data={data} />
                <HistorySessions data={data} />
            </main>
        </>
    );
}

export default HistoryPage;

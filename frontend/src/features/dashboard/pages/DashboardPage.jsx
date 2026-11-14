import DashboardView from "../components/DashboardView";
import { useDashboardPage } from "../hooks/useDashboardPage";

function DashboardPage() {
    const data = useDashboardPage();

    return <DashboardView data={data} />;
}

export default DashboardPage;

import { Link } from "react-router-dom";

function Header() {
    return (
        <header>
            <h1>Study Tracker</h1>

            <nav>
                <Link to="/">Dashboard</Link>
                <Link to="/history">History</Link>
            </nav>
        </header>
    );
}

export default Header;
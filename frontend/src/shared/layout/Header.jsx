import { Link, NavLink, useLocation } from "react-router-dom";
import "./Header.css";

function Header() {
    const { pathname } = useLocation();

    return (
        <header className="navbar">
            <div className="container navbar-inner">
                <Link
                    className="brand"
                    to="/"
                    aria-label="Study Tracker home"
                >
                    <span className="brand-mark" aria-hidden="true">
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M12 3v18" />
                            <path d="M5 7h14" />
                            <path d="M5 17h14" />
                        </svg>
                    </span>
                    <span>STUDY TRACKER</span>
                </Link>

                <nav className="nav-links" aria-label="Main navigation">
                    <NavLink
                        className={({ isActive }) =>
                            `nav-link${isActive ? " active" : ""}`
                        }
                        to="/"
                        end
                    >
                        Dashboard
                    </NavLink>

                    <NavLink
                        className={({ isActive }) =>
                            `nav-link${isActive ? " active" : ""}`
                        }
                        to="/history"
                    >
                        History
                    </NavLink>

                    {pathname === "/" && (
                        <a className="nav-link" href="#statistics-title">
                            Stats
                        </a>
                    )}

                </nav>
            </div>
        </header>
    );
}

export default Header;

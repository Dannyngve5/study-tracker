import { useState } from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import StudyTimer from "../components/StudyTimer";
import { useDashboardData } from "../features/dashboard/useDashboardData";
import { useStudyTimer } from "../features/study-sessions/useStudyTimer";
import "./Dashboard.css";

function Dashboard() {
    const [period, setPeriod] = useState("today");

    const timer = useStudyTimer();
    const {
        subjects,
        subSubjects,
        selectedSubject,
        setSelectedSubject,
        selectedSubSubject,
        setSelectedSubSubject,
        selectedSubjectObject,
        selectedSubSubjectObject,
        summary,
        catalogError,
        summaryError,
        summaryLoading,
        clearError,
        refreshSummary,
    } = useDashboardData();
    const subjectLocked = timer.isActive;

    async function handleStart() {
        clearError();

        const started = await timer.start(
            selectedSubjectObject?.id ?? "",
            selectedSubSubjectObject?.id ?? null
        );

        if (started) {
            refreshSummary();
        }
    }

    async function handlePause() {
        const updated = await timer.pause();

        if (updated) {
            refreshSummary();
        }
    }

    async function handleResume() {
        const updated = await timer.resume();

        if (updated) {
            refreshSummary();
        }
    }

    async function handleStop() {
        const updated = await timer.stop();

        if (updated) {
            refreshSummary();
        }
    }

    async function handleReset() {
        const resetSuccessful = await timer.reset();

        if (resetSuccessful) {
            refreshSummary();
        }
    }

    const periodSeconds = {
        today: summary?.today_seconds ?? 0,
        week: summary?.this_week_seconds ?? 0,
        month: summary?.this_month_seconds ?? 0,
        all: summary?.all_time_seconds ?? 0,
    };

    const periodSessions = {
        today: summary?.today_sessions ?? 0,
        week: summary?.this_week_sessions ?? 0,
        month: summary?.this_month_sessions ?? 0,
        all: summary?.all_time_sessions ?? 0,
    };

    const selectedSeconds = periodSeconds[period];
    const selectedSessions = periodSessions[period];

    const averageSessionSeconds = selectedSessions
        ? Math.floor(selectedSeconds / selectedSessions)
        : 0;

    const summaryUnavailable =
        summaryLoading || (!summary && Boolean(summaryError));

    function formatHours(seconds) {
        const total = Number(seconds) || 0;
        const hours = Math.floor(total / 3600);
        const minutes = Math.floor((total % 3600) / 60);

        return (
            <>
                {hours}
                <span className="stat-unit">h</span>
                {minutes > 0 && (
                    <>
                        {" "}
                        {minutes}
                        <span className="stat-unit">min</span>
                    </>
                )}
            </>
        );
    }

    async function handleMainTimerAction() {
        if (timer.isRunning) {
            await handlePause();
        } else if (timer.isPaused) {
            await handleResume();
        } else {
            await handleStart();
        }
    }

    return (
        <>
            <Header />

            <main id="dashboard">
                <section
                    className="intro"
                    aria-labelledby="intro-title"
                >
                    <h1 id="intro-title">
                        Good afternoon. Make time for{" "}
                        <span>what matters.</span>
                    </h1>
                </section>

                <section
                    className="focus-section"
                    aria-labelledby="focus-heading"
                >
                    <div className="focus-content">
                        <h2
                            className="focus-heading"
                            id="focus-heading"
                        >
                            Your focus session
                        </h2>

                        <StudyTimer
                            hours={timer.hours}
                            minutes={timer.minutes}
                            seconds={timer.seconds}
                        />

                        <div className="selectors">
                            <div className="selector-group">
                                <div className="selector-label-row">
                                    <label
                                        className="selector-label"
                                        htmlFor="subject"
                                    >
                                        Subject
                                    </label>
                                </div>

                                <div className="select-wrapper">
                                    <select
                                        className="selector"
                                        id="subject"
                                        name="subject"
                                        value={selectedSubject}
                                        disabled={subjectLocked}
                                        onChange={(event) => {
                                            setSelectedSubject(
                                                event.target.value
                                            );
                                            setSelectedSubSubject("");
                                        }}
                                    >
                                        <option value="" disabled>
                                            Choose a subject
                                        </option>

                                        {subjects.map((subject) => (
                                            <option
                                                key={subject.id}
                                                value={subject.id}
                                            >
                                                {subject.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="selector-group">
                                <div className="selector-label-row">
                                    <label
                                        className="selector-label"
                                        htmlFor="subsubject"
                                    >
                                        Sub-subject
                                        <span className="selector-optional">
                                            (Optional)
                                        </span>
                                    </label>
                                </div>

                                <div className="select-wrapper">
                                    <select
                                        className="selector"
                                        id="subsubject"
                                        name="subsubject"
                                        value={selectedSubSubject}
                                        disabled={
                                            !selectedSubject || subjectLocked
                                        }
                                        onChange={(event) =>
                                            setSelectedSubSubject(
                                                event.target.value
                                            )
                                        }
                                    >
                                        <option value="">
                                            Choose a sub-subject
                                        </option>

                                        {subSubjects.map((subSubject) => (
                                            <option
                                                key={subSubject.id}
                                                value={subSubject.id}
                                            >
                                                {subSubject.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="timer-actions">
                            <button
                                className="start-button"
                                type="button"
                                id="start-button"
                                onClick={handleMainTimerAction}
                                disabled={
                                    timer.loading ||
                                    timer.actionLoading ||
                                    (!timer.isActive && !selectedSubject)
                                }
                            >
                                <svg
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="1.8"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    aria-hidden="true"
                                >
                                    {timer.isRunning ? (
                                        <path d="M8 6h3v12H8zM14 6h3v12h-3z" />
                                    ) : (
                                        <path d="M8 5.5v13l10-6.5z" />
                                    )}
                                </svg>

                                <span>
                                    {timer.loading
                                        ? "Loading session..."
                                        : timer.isRunning
                                          ? "Pause session"
                                          : timer.isPaused
                                            ? "Resume session"
                                            : "Start session"}
                                </span>
                            </button>

                            {timer.isActive && (
                                <>
                                    <button
                                        className="start-button timer-secondary-button"
                                        type="button"
                                        onClick={handleStop}
                                        disabled={timer.actionLoading}
                                    >
                                        <svg
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="1.8"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            aria-hidden="true"
                                        >
                                            <rect
                                                x="6"
                                                y="6"
                                                width="12"
                                                height="12"
                                                rx="1"
                                            />
                                        </svg>

                                        <span>Stop</span>
                                    </button>

                                    <button
                                        className="start-button timer-secondary-button"
                                        type="button"
                                        onClick={handleReset}
                                        disabled={timer.actionLoading}
                                    >
                                        <svg
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="1.8"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            aria-hidden="true"
                                        >
                                            <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
                                            <path d="M3 3v5h5" />
                                        </svg>

                                        <span>Reset</span>
                                    </button>
                                </>
                            )}
                        </div>

                        {timer.error && (
                            <p className="error-message" role="alert">
                                {timer.error}
                            </p>
                        )}
                    </div>
                </section>

                <section
                    className="statistics-section"
                    aria-labelledby="statistics-title"
                >
                    <div className="statistics-content">
                        <div className="statistics-header">
                            <h2
                                className="section-title"
                                id="statistics-title"
                            >
                                Your progress
                            </h2>

                            <div
                                className="period-tabs"
                                aria-label="Statistics period"
                            >
                                {[
                                    ["today", "Today"],
                                    ["week", "This week"],
                                    ["month", "This month"],
                                    ["all", "All time"],
                                ].map(([value, label]) => (
                                    <button
                                        key={value}
                                        className={`period-tab${
                                            period === value ? " active" : ""
                                        }`}
                                        type="button"
                                        aria-pressed={period === value}
                                        onClick={() => setPeriod(value)}
                                    >
                                        {label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {summaryError && (
                            <p className="error-message" role="alert">
                                {summaryError}
                            </p>
                        )}

                        <div className="stats-grid">
                            <article className="stat-card">
                                <h3 className="stat-label">
                                    Total study time
                                </h3>

                                <p className="stat-value">
                                    {summaryUnavailable
                                        ? "..."
                                        : formatHours(periodSeconds[period])}
                                </p>

                                <p className="stat-detail">
                                    Time invested in learning selected subject
                                </p>
                            </article>

                            <article className="stat-card">
                                <h3 className="stat-label">
                                    Number of sessions
                                </h3>

                                <p className="stat-value">
                                    {summaryUnavailable ? "..." : selectedSessions}
                                </p>

                                <p className="stat-detail">
                                    Every session is a step forward
                                </p>
                            </article>

                            <article className="stat-card">
                                <h3 className="stat-label">
                                    Average session
                                </h3>

                                <p className="stat-value">
                                    {summaryUnavailable
                                        ? "..."
                                        : Math.floor(averageSessionSeconds / 60)}

                                    {!summaryUnavailable && (
                                        <span className="stat-unit">min</span>
                                    )}
                                </p>

                                <p className="stat-detail">
                                    Average time per session
                                </p>
                            </article>
                        </div>

                        <div className="activity-grid">
                            <section
                                className="activity-panel"
                                id="history"
                                aria-labelledby="recent-title"
                            >
                                <div className="activity-header">
                                    <h2
                                        className="activity-title"
                                        id="recent-title"
                                    >
                                        Recent sessions
                                    </h2>

                                    <Link
                                        className="view-all-link"
                                        to="/history"
                                    >
                                        View history
                                    </Link>
                                </div>

                                {summaryLoading ? (
                                    <p className="empty-state-description">
                                        Loading recent sessions...
                                    </p>
                                ) : summaryError && !summary ? (
                                    <p className="empty-state-description">
                                        Activity is unavailable.
                                    </p>
                                ) : summary?.recent_activity?.length ? (
                                    <div className="recent-sessions-list">
                                        {summary.recent_activity.map(
                                            (item) => (
                                                <article
                                                    className="recent-session"
                                                    key={item.session_id}
                                                >
                                                    <div>
                                                        <h3 className="empty-state-title">
                                                            {item.subject_name}
                                                        </h3>

                                                        <p className="empty-state-description">
                                                            {new Date(
                                                                item.started_at
                                                            ).toLocaleString()}
                                                        </p>
                                                    </div>

                                                    <p className="stat-value">
                                                        {formatHours(
                                                            item.duration_seconds
                                                        )}
                                                    </p>
                                                </article>
                                            )
                                        )}
                                    </div>
                                ) : (
                                    <div className="empty-state">
                                        <span
                                            className="empty-state-icon"
                                            aria-hidden="true"
                                        >
                                            <svg
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="1.5"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            >
                                                <circle
                                                    cx="12"
                                                    cy="12"
                                                    r="9"
                                                />
                                                <path d="M12 7v5l3 2" />
                                            </svg>
                                        </span>

                                        <h3 className="empty-state-title">
                                            Your story starts here.
                                        </h3>

                                        <p className="empty-state-description">
                                            Complete your first focus session
                                            and it will appear here, ready for
                                            you to look back on.
                                        </p>
                                    </div>
                                )}
                            </section>

                            <section
                                className="activity-panel"
                                aria-labelledby="top-subjects-title"
                            >
                                <div className="activity-header">
                                    <h2
                                        className="activity-title"
                                        id="top-subjects-title"
                                    >
                                        Top subjects
                                    </h2>
                                </div>

                                {summaryLoading ? (
                                    <p className="empty-state-description">
                                        Loading subject activity...
                                    </p>
                                ) : summaryError && !summary ? (
                                    <p className="empty-state-description">
                                        Activity is unavailable.
                                    </p>
                                ) : summary?.top_subjects?.length ? (
                                    <div className="subject-ranking">
                                        {summary.top_subjects.map((item) => (
                                            <div
                                                className="subject-ranking-item"
                                                key={item.subject_name}
                                            >
                                                <div className="subject-ranking-header">
                                                    <span className="subject-ranking-name">
                                                        {item.subject_name}
                                                    </span>

                                                    <span className="subject-ranking-time">
                                                        {formatHours(
                                                            item.duration_seconds
                                                        )}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="top-subjects-card">
                                        <div className="subjects-empty">
                                            <p>
                                                Your most studied subjects will
                                                appear here once you start
                                                tracking your time.
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </section>
                        </div>
                    </div>
                </section>
            </main>

            {catalogError && (
                <p role="alert" className="error-message">
                    {catalogError}
                </p>
            )}

            <footer className="footer">
                <div className="container footer-inner">
                    <span className="footer-brand">STUDY TRACKER</span>

                    <p className="footer-note">
                        Built for consistency, one session at a time.
                    </p>
                </div>
            </footer>
        </>
    );
}

export default Dashboard;
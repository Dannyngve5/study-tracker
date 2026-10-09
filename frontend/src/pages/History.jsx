import Header from "../components/Header";
import {
    HISTORY_GROUP_BY,
    HISTORY_MODES,
    HISTORY_PERIODS,
} from "../features/history/historyConstants";
import { useHistoryData } from "../features/history/useHistoryData";
import "./History.css";

const PERIOD_OPTIONS = [
    [HISTORY_PERIODS.ALL_TIME, "All Time"],
    [HISTORY_PERIODS.TODAY, "Today"],
    [HISTORY_PERIODS.THIS_WEEK, "This Week"],
    [HISTORY_PERIODS.THIS_MONTH, "This Month"],
    [HISTORY_PERIODS.LAST_7_DAYS, "Last 7 Days"],
    [HISTORY_PERIODS.LAST_30_DAYS, "Last 30 Days"],
    [HISTORY_PERIODS.CUSTOM, "Custom"],
];

const GROUP_BY_OPTIONS = [
    [HISTORY_GROUP_BY.DAY, "Day"],
    [HISTORY_GROUP_BY.WEEK, "Week"],
    [HISTORY_GROUP_BY.MONTH, "Month"],
];

function formatDuration(totalSeconds) {
    const seconds = totalSeconds ?? 0;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${hours}h ${minutes}m ${remainingSeconds}s`;
}

function HistoryFilters({ data }) {
    return (
        <>
            <section className="history-card">
                <h2>Filters</h2>

                <div className="history-filter-grid">
                    <div className="history-field">
                        <label htmlFor="history-subject">Subject</label>
                        <select
                            id="history-subject"
                            value={data.subjectId}
                            onChange={(event) =>
                                data.changeSubject(event.target.value)
                            }
                        >
                            <option value="">All Subjects</option>
                            {data.subjects.map((subject) => (
                                <option key={subject.id} value={subject.id}>
                                    {subject.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="history-field">
                        <label htmlFor="history-subsubject">SubSubject</label>
                        <select
                            id="history-subsubject"
                            value={data.subSubjectId}
                            disabled={!data.subjectId}
                            onChange={(event) =>
                                data.changeSubSubject(event.target.value)
                            }
                        >
                            <option value="">All SubSubjects</option>
                            {data.selectedSubSubjects.map((subSubject) => (
                                <option
                                    key={subSubject.id}
                                    value={subSubject.id}
                                >
                                    {subSubject.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="history-field">
                        <label htmlFor="history-period">Period</label>
                        <select
                            id="history-period"
                            value={data.period}
                            onChange={(event) =>
                                data.changePeriod(event.target.value)
                            }
                        >
                            {PERIOD_OPTIONS.map(([value, label]) => (
                                <option key={value} value={value}>
                                    {label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {data.period === HISTORY_PERIODS.CUSTOM && (
                        <div className="history-date-range">
                            <div className="history-field">
                                <label htmlFor="history-start-date">
                                    Start date
                                </label>
                                <input
                                    id="history-start-date"
                                    type="date"
                                    value={data.startDate}
                                    onChange={(event) =>
                                        data.changeStartDate(event.target.value)
                                    }
                                />
                            </div>

                            <div className="history-field">
                                <label htmlFor="history-end-date">
                                    End date
                                </label>
                                <input
                                    id="history-end-date"
                                    type="date"
                                    value={data.endDate}
                                    onChange={(event) =>
                                        data.changeEndDate(event.target.value)
                                    }
                                />
                            </div>
                        </div>
                    )}
                </div>
            </section>

            <section className="history-card">
                <h2>View</h2>

                <div className="history-filter-grid">
                    <div className="history-field">
                        <label htmlFor="history-mode">Mode</label>
                        <select
                            id="history-mode"
                            value={data.mode}
                            onChange={(event) =>
                                data.changeMode(event.target.value)
                            }
                        >
                            <option value={HISTORY_MODES.INDIVIDUAL}>
                                Individual sessions
                            </option>
                            <option value={HISTORY_MODES.GROUPED}>
                                Grouped
                            </option>
                        </select>
                    </div>

                    {data.mode === HISTORY_MODES.GROUPED && (
                        <div className="history-field">
                            <label htmlFor="history-group-by">Group by</label>
                            <select
                                id="history-group-by"
                                value={data.groupBy}
                                onChange={(event) =>
                                    data.changeGroupBy(event.target.value)
                                }
                            >
                                {GROUP_BY_OPTIONS.map(([value, label]) => (
                                    <option key={value} value={value}>
                                        {label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>
            </section>
        </>
    );
}

function IndividualSessions({ data }) {
    if (!data.result?.items?.length) {
        return <p className="history-status">No sessions found.</p>;
    }

    return (
        <>
            <div className="history-session-list">
                {data.result.items.map((session) => (
                    <article className="history-session" key={session.id}>
                        <h3>
                            {data.subjects.find(
                                (subject) => subject.id === session.subject_id
                            )?.name ?? "Unknown subject"}
                        </h3>
                        <p>{formatDuration(session.duration_seconds)}</p>
                        <p>{new Date(session.started_at).toLocaleString()}</p>
                    </article>
                ))}
            </div>

            <div className="history-pagination">
                <button
                    type="button"
                    disabled={data.offset === 0}
                    onClick={() =>
                        data.loadPage(Math.max(0, data.offset - data.pageSize))
                    }
                >
                    Previous
                </button>
                <button
                    type="button"
                    disabled={!data.result.has_more}
                    onClick={() =>
                        data.loadPage(data.offset + data.pageSize)
                    }
                >
                    Next
                </button>
            </div>
        </>
    );
}

function GroupedSessions({ groups }) {
    if (!groups?.length) {
        return (
            <p className="history-status">No grouped sessions found.</p>
        );
    }

    return (
        <div className="history-session-list">
            {groups.map((group) => (
                <article
                    className="history-session"
                    key={`${group.period_start}-${group.subject_id}`}
                >
                    <h3>{group.subject_name}</h3>
                    <p>
                        Period: {new Date(group.period_start).toLocaleString()}{" "}
                        – {new Date(group.period_end).toLocaleString()}
                    </p>
                    <p>Total: {formatDuration(group.duration_seconds)}</p>
                    <p>Sessions: {group.session_count}</p>
                </article>
            ))}
        </div>
    );
}

function HistorySessions({ data }) {
    return (
        <section className="history-card" aria-busy={data.loading}>
            <h2>Sessions</h2>

            {data.loading ? (
                <p className="history-status">Loading history...</p>
            ) : data.historyError ? null : data.mode ===
              HISTORY_MODES.INDIVIDUAL ? (
                <IndividualSessions data={data} />
            ) : (
                <GroupedSessions groups={data.result} />
            )}
        </section>
    );
}

function History() {
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

export default History;

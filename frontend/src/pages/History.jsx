import { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";
const TIMEZONE = Intl.DateTimeFormat().resolvedOptions().timeZone;

const PERIODS = {
    ALL_TIME: "all_time",
    TODAY: "today",
    THIS_WEEK: "this_week",
    THIS_MONTH: "this_month",
    LAST_7_DAYS: "last_7_days",
    LAST_30_DAYS: "last_30_days",
    CUSTOM: "custom",
};

const MODES = {
    INDIVIDUAL: "individual",
    GROUPED: "grouped",
};

const GROUP_BY = {
    DAY: "day",
    WEEK: "week",
    MONTH: "month",
};

function formatDuration(totalSeconds) {
    const seconds = totalSeconds ?? 0;

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${hours}h ${minutes}m ${remainingSeconds}s`;
}

function History() {
    const [subjects, setSubjects] = useState([]);

    const [subjectId, setSubjectId] = useState("");
    const [subSubjectId, setSubSubjectId] = useState("");

    const [period, setPeriod] = useState(PERIODS.ALL_TIME);
    const [mode, setMode] = useState(MODES.INDIVIDUAL);
    const [groupBy, setGroupBy] = useState(GROUP_BY.DAY);

    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    const [result, setResult] = useState(null);

    const [offset, setOffset] = useState(0);
    const [limit] = useState(50);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadSubjects() {
            try {
                const response = await fetch(`${API_URL}/subjects`);

                if (!response.ok) {
                    throw new Error("Could not load subjects.");
                }

                const data = await response.json();

                setSubjects(data);
            } catch (error) {
                setError(error.message);
            }
        }

        loadSubjects();
    }, []);

    async function loadHistory(nextOffset = 0) {
        try {
            setLoading(true);
            setError("");

            const params = new URLSearchParams();

            params.set("timezone", TIMEZONE);
            params.set("period", period);
            params.set("mode", mode);
            params.set("group_by", groupBy);
            params.set("offset", nextOffset);
            params.set("limit", limit);

            if (subjectId) {
                params.set("subject_id", subjectId);
            }

            if (subSubjectId) {
                params.set("sub_subject_id", subSubjectId);
            }

            if (period === PERIODS.CUSTOM) {
                if (startDate) {
                    params.set(
                        "start_date",
                        `${startDate}T00:00:00`
                    );
                }

                if (endDate) {
                    params.set(
                        "end_date",
                        `${endDate}T23:59:59`
                    );
                }
            }

            const response = await fetch(
                `${API_URL}/analytics/sessions?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error("Could not load history.");
            }

            const data = await response.json();

            setResult(data);
            setOffset(nextOffset);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadHistory(0);
    }, [
        subjectId,
        subSubjectId,
        period,
        mode,
        groupBy,
        startDate,
        endDate,
    ]);

    return (
        <main>
            <h1>History</h1>

            {error && <p>{error}</p>}

            <section>
                <h2>Filters</h2>

                <div>
                    <label htmlFor="history-subject">
                        Subject
                    </label>

                    <select
                        id="history-subject"
                        value={subjectId}
                        onChange={(event) =>
                            setSubjectId(event.target.value)
                        }
                    >
                        <option value="">
                            All Subjects
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

                <div>
                    <label htmlFor="history-subsubject">
                        Subsubject ID
                    </label>

                    <input
                        id="history-subsubject"
                        type="number"
                        min="1"
                        value={subSubjectId}
                        onChange={(event) =>
                            setSubSubjectId(event.target.value)
                        }
                        placeholder="Optional"
                    />
                </div>

                <div>
                    <label htmlFor="history-period">
                        Period
                    </label>

                    <select
                        id="history-period"
                        value={period}
                        onChange={(event) =>
                            setPeriod(event.target.value)
                        }
                    >
                        <option value="all_time">
                            All Time
                        </option>

                        <option value="today">
                            Today
                        </option>

                        <option value="this_week">
                            This Week
                        </option>

                        <option value="this_month">
                            This Month
                        </option>

                        <option value="last_7_days">
                            Last 7 Days
                        </option>

                        <option value="last_30_days">
                            Last 30 Days
                        </option>

                        <option value="custom">
                            Custom
                        </option>
                    </select>
                </div>

                {period === PERIODS.CUSTOM && (
                    <div>
                        <div>
                            <label htmlFor="history-start-date">
                                Start date
                            </label>

                            <input
                                id="history-start-date"
                                type="date"
                                value={startDate}
                                onChange={(event) =>
                                    setStartDate(
                                        event.target.value
                                    )
                                }
                            />
                        </div>

                        <div>
                            <label htmlFor="history-end-date">
                                End date
                            </label>

                            <input
                                id="history-end-date"
                                type="date"
                                value={endDate}
                                onChange={(event) =>
                                    setEndDate(
                                        event.target.value
                                    )
                                }
                            />
                        </div>
                    </div>
                )}
            </section>

            <section>
                <h2>View</h2>

                <div>
                    <label htmlFor="history-mode">
                        Mode
                    </label>

                    <select
                        id="history-mode"
                        value={mode}
                        onChange={(event) =>
                            setMode(event.target.value)
                        }
                    >
                        <option value="individual">
                            Individual sessions
                        </option>

                        <option value="grouped">
                            Grouped
                        </option>
                    </select>
                </div>

                {mode === MODES.GROUPED && (
                    <div>
                        <label htmlFor="history-group-by">
                            Group by
                        </label>

                        <select
                            id="history-group-by"
                            value={groupBy}
                            onChange={(event) =>
                                setGroupBy(event.target.value)
                            }
                        >
                            <option value="day">
                                Day
                            </option>

                            <option value="week">
                                Week
                            </option>

                            <option value="month">
                                Month
                            </option>
                        </select>
                    </div>
                )}
            </section>

            <section>
                <h2>Sessions</h2>

                {loading ? (
                    <p>Loading history...</p>
                ) : mode === MODES.INDIVIDUAL ? (
                    <>
                        {result?.items?.length ? (
                            <div>
                                {result.items.map((session) => (
                                    <article key={session.id}>
                                        <h3>
                                            {session.subject_name}
                                        </h3>

                                        <p>
                                            {formatDuration(
                                                session.duration_seconds
                                            )}
                                        </p>

                                        <p>
                                            {new Date(
                                                session.started_at
                                            ).toLocaleString()}
                                        </p>
                                    </article>
                                ))}
                            </div>
                        ) : (
                            <p>No sessions found.</p>
                        )}

                        {result && (
                            <div>
                                <button
                                    disabled={offset === 0}
                                    onClick={() =>
                                        loadHistory(
                                            Math.max(
                                                0,
                                                offset - limit
                                            )
                                        )
                                    }
                                >
                                    Previous
                                </button>

                                <button
                                    disabled={!result.has_more}
                                    onClick={() =>
                                        loadHistory(
                                            offset + limit
                                        )
                                    }
                                >
                                    Next
                                </button>
                            </div>
                        )}
                    </>
                ) : (
                    <>
                        {result?.length ? (
                            <div>
                                {result.map((group) => (
                                    <article
                                        key={`${group.period_start}-${group.subject_id}`}
                                    >
                                        <h3>
                                            {group.subject_name}
                                        </h3>

                                        <p>
                                            Period:{" "}
                                            {new Date(
                                                group.period_start
                                            ).toLocaleString()}{" "}
                                            –{" "}
                                            {new Date(
                                                group.period_end
                                            ).toLocaleString()}
                                        </p>

                                        <p>
                                            Total:{" "}
                                            {formatDuration(
                                                group.duration_seconds
                                            )}
                                        </p>

                                        <p>
                                            Sessions:{" "}
                                            {group.session_count}
                                        </p>
                                    </article>
                                ))}
                            </div>
                        ) : (
                            <p>No grouped sessions found.</p>
                        )}
                    </>
                )}
            </section>
        </main>
    );
}

export default History;
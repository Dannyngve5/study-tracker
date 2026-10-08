import { useEffect, useState } from "react";
import StudyTimer from "../components/StudyTimer";
import Header from "../components/Header";

const API_URL = "http://localhost:8000";
const TIMEZONE = Intl.DateTimeFormat().resolvedOptions().timeZone;

function formatDuration(totalSeconds) {
    const seconds = totalSeconds ?? 0;

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    return `${hours}h ${minutes}m`;
}

function Dashboard() {
    const [subjects, setSubjects] = useState([]);
    const [selectedSubject, setSelectedSubject] = useState(null);
    const [summarySubjectId, setSummarySubjectId] = useState("");

    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [summaryLoading, setSummaryLoading] = useState(false);
    const [error, setError] = useState("");
    const [subjectLocked, setSubjectLocked] = useState(false);

    useEffect(() => {
        async function loadSubjects() {
            try {
                const response = await fetch(`${API_URL}/subjects`);

                if (!response.ok) {
                    throw new Error("Could not load subjects.");
                }

                const data = await response.json();

                setSubjects(data);

                if (data.length > 0) {
                    setSelectedSubject(data[0]);
                }
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        loadSubjects();
    }, []);

    useEffect(() => {
        async function loadSummary() {
            try {
                setSummaryLoading(true);
                setError("");

                const params = new URLSearchParams();

                params.set("timezone", TIMEZONE);

                if (summarySubjectId) {
                    params.set("subject_id", summarySubjectId);
                }

                const response = await fetch(
                    `${API_URL}/analytics/summary?${params.toString()}`
                );

                if (!response.ok) {
                    throw new Error("Could not load analytics.");
                }

                const data = await response.json();

                setSummary(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setSummaryLoading(false);
            }
        }

        loadSummary();
    }, [summarySubjectId]);

    async function handleCreateSubject(event) {
        event.preventDefault();

        const name = event.target.elements.subjectName.value.trim();

        if (!name) {
            return;
        }

        try {
            setError("");

            const response = await fetch(`${API_URL}/subjects`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name,
                }),
            });

            if (!response.ok) {
                if (response.status === 409) {
                    throw new Error(
                        "A subject with this name already exists."
                    );
                }

                throw new Error("Could not create subject.");
            }

            const subject = await response.json();

            setSubjects((previous) => [...previous, subject]);
            setSelectedSubject(subject);
            event.target.reset();
        } catch (error) {
            setError(error.message);
        }
    }

    if (loading) {
        return <p>Loading dashboard...</p>;
    }

    return (
    <>
        <Header />

        <main>
            <h1>Dashboard</h1>

            {error && <p>{error}</p>}

            <section>
                <h2>Timer</h2>

                <form onSubmit={handleCreateSubject}>
                    <input
                        name="subjectName"
                        type="text"
                        placeholder="New subject"
                    />

                    <button type="submit">
                        Create subject
                    </button>
                </form>

                <div>
                    <label htmlFor="timer-subject">
                        Subject
                    </label>

                    <select
                        id="timer-subject"
                        value={selectedSubject?.id ?? ""}
                        disabled={subjectLocked}
                        onChange={(event) => {
                            const subject = subjects.find(
                                (item) =>
                                    item.id ===
                                    Number(event.target.value)
                            );

                            setSelectedSubject(subject ?? null);
                        }}
                    >
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

                <StudyTimer
                    selectedSubject={selectedSubject}
                    onSubjectLockedChange={setSubjectLocked}
                />
            </section>

            <section>
                <h2>Summary</h2>

                <div>
                    <label htmlFor="summary-subject">
                        Subject
                    </label>

                    <select
                        id="summary-subject"
                        value={summarySubjectId}
                        onChange={(event) =>
                            setSummarySubjectId(event.target.value)
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

                {summaryLoading ? (
                    <p>Loading summary...</p>
                ) : (
                    <div>
                        <article>
                            <h3>Today</h3>
                            <p>
                                {formatDuration(
                                    summary?.today_seconds
                                )}
                            </p>
                        </article>

                        <article>
                            <h3>Week</h3>
                            <p>
                                {formatDuration(
                                    summary?.this_week_seconds
                                )}
                            </p>
                        </article>

                        <article>
                            <h3>All Time</h3>
                            <p>
                                {formatDuration(
                                    summary?.all_time_seconds
                                )}
                            </p>
                        </article>
                    </div>
                )}
            </section>

            <section>
                <h2>Top Subjects</h2>

                {summary?.top_subjects?.length ? (
                    <div>
                        {summary.top_subjects.map((subject) => (
                            <article key={subject.subject_name}>
                                <h3>{subject.subject_name}</h3>

                                <p>
                                    {formatDuration(
                                        subject.duration_seconds
                                    )}
                                </p>
                            </article>
                        ))}
                    </div>
                ) : (
                    <p>No study data yet.</p>
                )}
            </section>

            <section>
                <h2>Last Activity</h2>

                {summary?.recent_activity?.length ? (
                    <div>
                        {summary.recent_activity.map((activity) => (
                            <article key={activity.session_id}>
                                <h3>{activity.subject_name}</h3>

                                <p>
                                    {formatDuration(
                                        activity.duration_seconds
                                    )}
                                </p>

                                <p>
                                    {new Date(
                                        activity.started_at
                                    ).toLocaleString()}
                                </p>
                            </article>
                        ))}
                    </div>
                ) : (
                    <p>No recent activity.</p>
                )}
            </section>
        </main>
    </>
);
}

export default Dashboard;
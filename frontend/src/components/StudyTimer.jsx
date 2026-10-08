import { useEffect, useRef, useState } from "react";

const API_URL = "http://localhost:8000";

function StudyTimer({ selectedSubject }) {
    const [session, setSession] = useState(null);
    const [now, setNow] = useState(Date.now());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const intervalRef = useRef(null);

    const isActive =
        session?.status === "running" ||
        session?.status === "paused";

    useEffect(() => {
        async function loadActiveSession() {
            try {
                const response = await fetch(
                    `${API_URL}/study-sessions/active`
                );

                if (!response.ok) {
                    throw new Error("Could not load active session.");
                }

                const data = await response.json();

                setSession(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        loadActiveSession();
    }, []);

    useEffect(() => {
        if (session?.status !== "running") {
            return;
        }

        intervalRef.current = setInterval(() => {
            setNow(Date.now());
        }, 250);

        return () => {
            clearInterval(intervalRef.current);
        };
    }, [session?.status]);

    function getElapsedSeconds() {
        if (!session) {
            return 0;
        }

        const startedAt = new Date(session.started_at).getTime();
        const pausedDuration = session.paused_duration_seconds ?? 0;

        if (session.status === "running") {
            return Math.max(
                0,
                Math.floor(
                    (now - startedAt) / 1000 - pausedDuration
                )
            );
        }

        if (session.status === "paused") {
            const pausedAt = new Date(session.paused_at).getTime();

            return Math.max(
                0,
                Math.floor(
                    (pausedAt - startedAt) / 1000 - pausedDuration
                )
            );
        }

        if (session.status === "finished") {
            return session.duration_seconds ?? 0;
        }

        return 0;
    }

    const totalSeconds = getElapsedSeconds();

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    async function handleStart() {
        if (!selectedSubject) {
            return;
        }

        try {
            setError("");

            const response = await fetch(
                `${API_URL}/study-sessions/start`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        subject_id: selectedSubject.id,
                    }),
                }
            );

            if (!response.ok) {
                if (response.status === 409) {
                    throw new Error(
                        "There is already an active study session."
                    );
                }

                throw new Error("Could not start study session.");
            }

            const data = await response.json();

            setSession(data);
            setNow(Date.now());
        } catch (error) {
            setError(error.message);
        }
    }

    async function handlePause() {
        if (!session) {
            return;
        }

        try {
            setError("");

            const response = await fetch(
                `${API_URL}/study-sessions/${session.id}/pause`,
                {
                    method: "POST",
                }
            );

            if (!response.ok) {
                throw new Error("Could not pause study session.");
            }

            const data = await response.json();

            setSession(data);
            setNow(Date.now());
        } catch (error) {
            setError(error.message);
        }
    }

    async function handleResume() {
        if (!session) {
            return;
        }

        try {
            setError("");

            const response = await fetch(
                `${API_URL}/study-sessions/${session.id}/resume`,
                {
                    method: "POST",
                }
            );

            if (!response.ok) {
                throw new Error("Could not resume study session.");
            }

            const data = await response.json();

            setSession(data);
            setNow(Date.now());
        } catch (error) {
            setError(error.message);
        }
    }

    async function handleStop() {
        if (!session) {
            return;
        }

        try {
            setError("");

            const response = await fetch(
                `${API_URL}/study-sessions/${session.id}/stop`,
                {
                    method: "POST",
                }
            );

            if (!response.ok) {
                throw new Error("Could not stop study session.");
            }

            const data = await response.json();

            setSession(data);
            setNow(Date.now());
        } catch (error) {
            setError(error.message);
        }
    }

    async function handleReset() {
        if (!session) {
            setNow(Date.now());
            return;
        }

        try {
            setError("");

            if (
                session.status === "running" ||
                session.status === "paused"
            ) {
                const stopResponse = await fetch(
                    `${API_URL}/study-sessions/${session.id}/stop`,
                    {
                        method: "POST",
                    }
                );

                if (!stopResponse.ok) {
                    throw new Error("Could not reset study session.");
                }
            }

            const deleteResponse = await fetch(
                `${API_URL}/study-sessions/${session.id}`,
                {
                    method: "DELETE",
                }
            );

            if (!deleteResponse.ok) {
                throw new Error("Could not reset study session.");
            }

            setSession(null);
            setNow(Date.now());
        } catch (error) {
            setError(error.message);
        }
    }

    if (loading) {
        return <p>Loading timer...</p>;
    }

    return (
        <div className="study-timer">
            <div className="tags-container">
                {selectedSubject && (
                    <span className="subject-tag">
                        {selectedSubject.name}
                    </span>
                )}
            </div>

            {error && <p>{error}</p>}

            <div className="timer-container">
                <div className="timer-display">
                    <span className="hours">
                        {String(hours).padStart(2, "0")}
                    </span>

                    <span>:</span>

                    <span className="minutes">
                        {String(minutes).padStart(2, "0")}
                    </span>

                    <span>:</span>

                    <span className="seconds">
                        {String(seconds).padStart(2, "0")}
                    </span>
                </div>
            </div>

            <div className="buttons-container">
                {!isActive && (
                    <button
                        className="start-button"
                        onClick={handleStart}
                        disabled={!selectedSubject}
                    >
                        Start
                    </button>
                )}

                {session?.status === "running" && (
                    <>
                        <button
                            className="pause-button"
                            onClick={handlePause}
                        >
                            Pause
                        </button>

                        <button
                            className="reset-button"
                            onClick={handleReset}
                        >
                            Reset
                        </button>

                        <button
                            className="stop-button"
                            onClick={handleStop}
                        >
                            Stop
                        </button>
                    </>
                )}

                {session?.status === "paused" && (
                    <>
                        <button
                            className="resume-button"
                            onClick={handleResume}
                        >
                            Resume
                        </button>

                        <button
                            className="reset-button"
                            onClick={handleReset}
                        >
                            Reset
                        </button>

                        <button
                            className="stop-button"
                            onClick={handleStop}
                        >
                            Stop
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}

export default StudyTimer;
import { useEffect, useRef, useState } from "react";

function StudyTimer({ selectedSubject }) {
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const [status, setStatus] = useState("idle");
    const [now, setNow] = useState(Date.now());

    const startTimeRef = useRef(null);

    useEffect(() => {
        if (status !== "running") {
            return;
        }

        const interval = setInterval(() => {
            setNow(Date.now());
        }, 250);

        return () => {
            clearInterval(interval);
        };
    }, [status]);

    let totalSeconds = elapsedSeconds;

    if (status === "running" && startTimeRef.current !== null) {
        const currentSegment = Math.floor(
            (now - startTimeRef.current) / 1000
        );

        totalSeconds += currentSegment;
    }

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    function handleStart() {
        startTimeRef.current = Date.now();
        setNow(Date.now());
        setStatus("running");
    }

    function handlePause() {
        if (startTimeRef.current === null) {
            return;
        }

        const currentSegment = Math.floor(
            (Date.now() - startTimeRef.current) / 1000
        );

        setElapsedSeconds((previous) => previous + currentSegment);

        startTimeRef.current = null;
        setNow(Date.now());
        setStatus("paused");
    }

    function handleResume() {
        startTimeRef.current = Date.now();
        setNow(Date.now());
        setStatus("running");
    }

    function handleReset() {
        startTimeRef.current = null;
        setElapsedSeconds(0);
        setNow(Date.now());
        setStatus("idle");
    }

    function handleStop() {
        let finalSeconds = elapsedSeconds;

        if (status === "running" && startTimeRef.current !== null) {
            const currentSegment = Math.floor(
                (Date.now() - startTimeRef.current) / 1000
            );

            finalSeconds += currentSegment;
        }

        console.log("Session finished:", {
            subject: selectedSubject,
            durationSeconds: finalSeconds,
        });

        startTimeRef.current = null;
        setElapsedSeconds(finalSeconds);
        setNow(Date.now());
        setStatus("idle");
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

                {status === "idle" && (
                    <button
                        className="start-button"
                        onClick={handleStart}
                        disabled={!selectedSubject}
                    >
                        Start
                    </button>
                )}

                {status === "running" && (
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

                {status === "paused" && (
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
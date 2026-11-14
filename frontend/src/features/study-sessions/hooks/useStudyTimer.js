import { useCallback, useEffect, useRef, useState } from "react";
import {
    deleteStudySession,
    getActiveSession,
    pauseStudySession,
    resumeStudySession,
    startStudySession,
    stopStudySession,
} from "../api/studySessionsApi";

export function useStudyTimer() {
    const [session, setSession] = useState(null);
    const [now, setNow] = useState(0);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState("");
    const actionInProgressRef = useRef(false);

    useEffect(() => {
        const controller = new AbortController();

        async function loadSession() {
            try {
                const data = await getActiveSession({
                    signal: controller.signal,
                });

                setSession(data);
                setNow(Date.now());
            } catch (err) {
                if (err.name !== "AbortError") {
                    setError(err.message);
                }
            } finally {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        }

        loadSession();

        return () => controller.abort();
    }, []);

    useEffect(() => {
        if (session?.status !== "running") {
            return undefined;
        }

        const intervalId = window.setInterval(() => {
            setNow(Date.now());
        }, 250);

        return () => window.clearInterval(intervalId);
    }, [session?.status]);

    const elapsedSeconds = (() => {
        if (!session) {
            return 0;
        }

        if (session.status === "finished") {
            return session.duration_seconds ?? 0;
        }

        const startedAt = new Date(session.started_at).getTime();
        const pausedDuration = session.paused_duration_seconds ?? 0;

        if (session.status === "running") {
            return Math.max(
                0,
                Math.floor((now - startedAt) / 1000 - pausedDuration)
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

        return 0;
    })();

    const hours = Math.floor(elapsedSeconds / 3600);
    const minutes = Math.floor((elapsedSeconds % 3600) / 60);
    const seconds = elapsedSeconds % 60;

    const isRunning = session?.status === "running";
    const isPaused = session?.status === "paused";
    const isFinished = session?.status === "finished";
    const isActive = isRunning || isPaused;

    const runAction = useCallback(async (action, onSuccess = (result) => {
        setSession(result);
        setNow(Date.now());
    }) => {
        if (actionInProgressRef.current) {
            return null;
        }

        actionInProgressRef.current = true;
        setActionLoading(true);
        setError("");

        try {
            const result = await action();
            onSuccess(result);

            return result;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            actionInProgressRef.current = false;
            setActionLoading(false);
        }
    }, []);

    const start = useCallback(
        async (subjectId, subSubjectId = null) => {
            if (!subjectId) {
                setError("Choose a subject before starting a session.");
                return null;
            }

            if (isActive) {
                setError(
                    "Stop the current session before starting another."
                );
                return null;
            }

            return runAction(() =>
                startStudySession(subjectId, subSubjectId)
            );
        },
        [isActive, runAction]
    );

    const pause = useCallback(async () => {
        if (!session || !isRunning) {
            return null;
        }

        return runAction(() => pauseStudySession(session.id));
    }, [session, isRunning, runAction]);

    const resume = useCallback(async () => {
        if (!session || !isPaused) {
            return null;
        }

        return runAction(() => resumeStudySession(session.id));
    }, [session, isPaused, runAction]);

    const stop = useCallback(async () => {
        if (!session || !isActive) {
            return null;
        }

        return runAction(
            () => stopStudySession(session.id),
            (updatedSession) => {
                setSession(updatedSession);
                setNow(Date.now());
            }
        );
    }, [session, isActive, runAction]);

    const reset = useCallback(async () => {
        const resetSuccessful = await runAction(async () => {
            if (isActive && session) {
                await deleteStudySession(session.id);
            }

            return true;
        }, () => {
            setSession(null);
            setNow(Date.now());
        });

        return resetSuccessful === true;
    }, [session, isActive, runAction]);

    return {
        session,
        loading,
        actionLoading,
        error,
        elapsedSeconds,
        hours,
        minutes,
        seconds,
        isRunning,
        isPaused,
        isFinished,
        isActive,
        start,
        pause,
        resume,
        stop,
        reset,
    };
}
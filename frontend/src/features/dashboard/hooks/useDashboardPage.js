import { useState } from "react";
import { useDashboardData } from "./useDashboardData";
import { useStudyTimer } from "../../study-sessions/hooks/useStudyTimer";

export function useDashboardPage() {
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

    async function handleMainTimerAction() {
        if (timer.isRunning) {
            await handlePause();
        } else if (timer.isPaused) {
            await handleResume();
        } else {
            await handleStart();
        }
    }

    return {
        period,
        setPeriod,
        timer,
        subjects,
        subSubjects,
        selectedSubject,
        setSelectedSubject,
        selectedSubSubject,
        setSelectedSubSubject,
        summary,
        catalogError,
        summaryError,
        summaryLoading,
        periodSeconds,
        selectedSessions,
        averageSessionSeconds,
        summaryUnavailable,
        handleStart,
        handlePause,
        handleResume,
        handleStop,
        handleReset,
        handleMainTimerAction,
    };
}

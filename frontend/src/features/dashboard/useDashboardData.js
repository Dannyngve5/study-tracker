import { useCallback, useEffect, useState } from "react";
import { getStudySummary } from "../analytics/analyticsApi";
import {
    getSubjects,
    getSubSubjects,
} from "../subjects/subjectsApi";

const TIMEZONE = Intl.DateTimeFormat().resolvedOptions().timeZone;

export function useDashboardData() {
    const [subjects, setSubjects] = useState([]);
    const [subSubjects, setSubSubjects] = useState([]);
    const [selectedSubject, setSelectedSubject] = useState("");
    const [selectedSubSubject, setSelectedSubSubject] = useState("");
    const [summary, setSummary] = useState(null);
    const [catalogError, setCatalogError] = useState("");
    const [summaryError, setSummaryError] = useState("");
    const [refreshKey, setRefreshKey] = useState(0);
    const [loadedSummaryKey, setLoadedSummaryKey] = useState(null);
    const summaryRequestKey = `${selectedSubject}:${refreshKey}`;

    const selectedSubjectObject =
        subjects.find(
            (item) => String(item.id) === selectedSubject
        ) ?? null;
    const selectedSubSubjectObject =
        subSubjects.find(
            (item) => String(item.id) === selectedSubSubject
        ) ?? null;

    useEffect(() => {
        const controller = new AbortController();

        async function loadSubjects() {
            setCatalogError("");
            try {
                const data = await getSubjects({
                    signal: controller.signal,
                });

                setSubjects(data);
                setCatalogError("");
                setSelectedSubject((current) => {
                    if (
                        current &&
                        data.some((item) => String(item.id) === current)
                    ) {
                        return current;
                    }

                    return data.length > 0 ? String(data[0].id) : "";
                });
            } catch (requestError) {
                if (!controller.signal.aborted) {
                    setCatalogError(requestError.message);
                }
            }
        }

        loadSubjects();

        return () => controller.abort();
    }, []);

    useEffect(() => {
        const controller = new AbortController();

        async function loadSubSubjects() {
            setCatalogError("");
            if (!selectedSubject) {
                setSubSubjects([]);
                setSelectedSubSubject("");
                return;
            }

            try {
                const data = await getSubSubjects({
                    signal: controller.signal,
                });
                const filtered = data.filter(
                    (item) => String(item.subject_id) === selectedSubject
                );

                setSubSubjects(filtered);
                setCatalogError("");
                setSelectedSubSubject((current) =>
                    filtered.some((item) => String(item.id) === current)
                        ? current
                        : ""
                );
            } catch (requestError) {
                if (!controller.signal.aborted) {
                    setCatalogError(requestError.message);
                }
            }
        }

        loadSubSubjects();

        return () => controller.abort();
    }, [selectedSubject]);

    const loadSummary = useCallback(
        async (signal) => {
            const data = await getStudySummary({
                timezone: TIMEZONE,
                subjectId: selectedSubject,
                signal,
            });

            setSummary(data);
        },
        [selectedSubject]
    );

    useEffect(() => {
        const controller = new AbortController();

        async function load() {
            try {
                await loadSummary(controller.signal);
                setSummaryError("");
            } catch (requestError) {
                if (!controller.signal.aborted) {
                    setSummaryError(requestError.message);
                }
            } finally {
                if (!controller.signal.aborted) {
                    setLoadedSummaryKey(summaryRequestKey);
                }
            }
        }

        load();

        return () => controller.abort();
    }, [loadSummary, refreshKey, summaryRequestKey]);

    const refreshSummary = useCallback(() => {
        setRefreshKey((current) => current + 1);
    }, []);

    const clearError = useCallback(() => {
        setCatalogError("");
        setSummaryError("");
    }, []);

    return {
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
        summaryLoading: loadedSummaryKey !== summaryRequestKey,
        clearError,
        refreshSummary,
    };
}

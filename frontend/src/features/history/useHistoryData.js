import { useEffect, useState } from "react";
import {
    getSubjects,
    getSubSubjects,
} from "../subjects/subjectsApi";
import { getHistory } from "./historyApi";
import {
    HISTORY_GROUP_BY,
    HISTORY_MODES,
    HISTORY_PERIODS,
} from "./historyConstants";

const TIMEZONE = Intl.DateTimeFormat().resolvedOptions().timeZone;
const PAGE_SIZE = 50;

export function useHistoryData() {
    const [subjects, setSubjects] = useState([]);
    const [subSubjects, setSubSubjects] = useState([]);
    const [subjectId, setSubjectId] = useState("");
    const [subSubjectId, setSubSubjectId] = useState("");
    const [period, setPeriod] = useState(HISTORY_PERIODS.ALL_TIME);
    const [mode, setMode] = useState(HISTORY_MODES.INDIVIDUAL);
    const [groupBy, setGroupBy] = useState(HISTORY_GROUP_BY.DAY);
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [result, setResult] = useState(null);
    const [offset, setOffset] = useState(0);
    const [loading, setLoading] = useState(true);
    const [catalogError, setCatalogError] = useState("");
    const [historyError, setHistoryError] = useState("");

    useEffect(() => {
        const controller = new AbortController();

        async function loadSubjects() {
            try {
                setSubjects(
                    await getSubjects({ signal: controller.signal })
                );
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
            try {
                setSubSubjects(
                    await getSubSubjects({ signal: controller.signal })
                );
            } catch (requestError) {
                if (!controller.signal.aborted) {
                    setCatalogError(requestError.message);
                    setSubSubjects([]);
                }
            }
        }

        loadSubSubjects();

        return () => controller.abort();
    }, []);

    useEffect(() => {
        const controller = new AbortController();

        async function loadHistory() {
            try {
                setResult(
                    await getHistory({
                        timezone: TIMEZONE,
                        period,
                        mode,
                        groupBy,
                        startDate,
                        endDate,
                        subjectId,
                        subSubjectId,
                        offset,
                        limit: PAGE_SIZE,
                        signal: controller.signal,
                    })
                );
                setHistoryError("");
            } catch (requestError) {
                if (!controller.signal.aborted) {
                    setHistoryError(requestError.message);
                }
            } finally {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        }

        loadHistory();

        return () => controller.abort();
    }, [
        subjectId,
        subSubjectId,
        period,
        mode,
        groupBy,
        startDate,
        endDate,
        offset,
    ]);

    function updateFilters(update) {
        setLoading(true);
        setHistoryError("");
        setResult(null);
        setOffset(0);
        update();
    }

    function loadPage(nextOffset) {
        setLoading(true);
        setHistoryError("");
        setResult(null);
        setOffset(nextOffset);
    }

    function changeSubject(value) {
        updateFilters(() => {
            setSubjectId(value);
            setSubSubjectId("");
        });
    }

    const selectedSubSubjects = subSubjects.filter(
        (subSubject) => subSubject.subject_id === Number(subjectId)
    );

    return {
        subjects,
        selectedSubSubjects,
        subjectId,
        subSubjectId,
        period,
        mode,
        groupBy,
        startDate,
        endDate,
        result,
        offset,
        pageSize: PAGE_SIZE,
        loading,
        catalogError,
        historyError,
        changeSubject,
        changeSubSubject: (value) =>
            updateFilters(() => setSubSubjectId(value)),
        changePeriod: (value) => updateFilters(() => setPeriod(value)),
        changeMode: (value) => updateFilters(() => setMode(value)),
        changeGroupBy: (value) => updateFilters(() => setGroupBy(value)),
        changeStartDate: (value) => updateFilters(() => setStartDate(value)),
        changeEndDate: (value) => updateFilters(() => setEndDate(value)),
        loadPage,
    };
}

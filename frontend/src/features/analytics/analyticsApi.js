import { apiRequest } from "../../api/client";

export function getStudySummary({
    timezone,
    subjectId,
    signal,
}) {
    const params = new URLSearchParams({ timezone });

    if (subjectId) {
        params.set("subject_id", String(subjectId));
    }

    return apiRequest(
        `/analytics/summary?${params.toString()}`,
        { signal }
    );
}
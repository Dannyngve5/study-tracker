import { apiRequest } from "../../../shared/api/client";

export function getHistory({
    timezone,
    period,
    mode,
    groupBy,
    startDate,
    endDate,
    subjectId,
    subSubjectId,
    offset,
    limit,
    signal,
}) {
    const params = new URLSearchParams({
        timezone,
        period,
        mode,
        group_by: groupBy,
        offset: String(offset),
        limit: String(limit),
    });

    if (subjectId) {
        params.set("subject_id", subjectId);
    }

    if (subSubjectId) {
        params.set("sub_subject_id", subSubjectId);
    }

    if (period === "custom") {
        if (startDate) {
            params.set("start_date", `${startDate}T00:00:00`);
        }

        if (endDate) {
            params.set("end_date", `${endDate}T23:59:59`);
        }
    }

    return apiRequest(`/analytics/sessions?${params.toString()}`, {
        signal,
    });
}
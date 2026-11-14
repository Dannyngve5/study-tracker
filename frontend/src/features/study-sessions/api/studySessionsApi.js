import { apiRequest, jsonOptions } from "../../../shared/api/client";

export function getActiveSession({ signal } = {}) {
    return apiRequest("/study-sessions/active", { signal });
}

export function startStudySession(subjectId, subSubjectId = null) {
    return apiRequest(
        "/study-sessions/start",
        jsonOptions("POST", {
            subject_id: Number(subjectId),
            sub_subject_id:
                subSubjectId === "" || subSubjectId == null
                    ? null
                    : Number(subSubjectId),
        })
    );
}

export function pauseStudySession(sessionId) {
    return apiRequest(
        `/study-sessions/${sessionId}/pause`,
        jsonOptions("POST")
    );
}

export function resumeStudySession(sessionId) {
    return apiRequest(
        `/study-sessions/${sessionId}/resume`,
        jsonOptions("POST")
    );
}

export function stopStudySession(sessionId) {
    return apiRequest(
        `/study-sessions/${sessionId}/stop`,
        jsonOptions("POST")
    );
}

export function deleteStudySession(sessionId) {
    return apiRequest(
        `/study-sessions/${sessionId}`,
        { method: "DELETE" }
    );
}
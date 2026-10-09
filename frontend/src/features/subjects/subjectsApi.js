import { apiRequest } from "../../api/client";

export function getSubjects({ signal } = {}) {
    return apiRequest("/subjects/", { signal });
}

export function getSubSubjects({ signal } = {}) {
    return apiRequest("/sub-subjects/", { signal });
}
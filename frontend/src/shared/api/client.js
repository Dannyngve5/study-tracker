
const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL ||
    (import.meta.env.DEV ? "http://localhost:8000" : "")
).replace(/\/+$/, "");

if (!API_BASE_URL) {
    throw new Error("VITE_API_BASE_URL must be configured.");
}

export async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
            Accept: "application/json",
            ...options.headers,
        },
    });

    if (response.status === 204) {
        return null;
    }

    const body = await response.text();
    let data = null;

    if (body) {
        try {
            data = JSON.parse(body);
        } catch (error) {
            if (response.ok) {
                throw new Error("The server returned an invalid JSON response.", {
                    cause: error,
                });
            }
        }
    }

    if (!response.ok) {
        const detail = data?.detail ?? data?.message;
        const message =
            typeof detail === "string" && detail.trim()
                ? detail
                : detail === undefined
                  ? `Request failed (${response.status}).`
                  : JSON.stringify(detail);

        throw new Error(message);
    }

    if (!body) {
        return null;
    }

    return data;
}

export function jsonOptions(method, body) {
    return {
        method,
        headers: {
            "Content-Type": "application/json",
        },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    };
}
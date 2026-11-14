import {
    HISTORY_MODES,
} from "../model/historyConstants";

function formatDuration(totalSeconds) {
    const seconds = totalSeconds ?? 0;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${hours}h ${minutes}m ${remainingSeconds}s`;
}

function IndividualSessions({ data }) {
    if (!data.result?.items?.length) {
        return <p className="history-status">No sessions found.</p>;
    }

    return (
        <>
            <div className="history-session-list">
                {data.result.items.map((session) => (
                    <article className="history-session" key={session.id}>
                        <h3>
                            {data.subjects.find(
                                (subject) => subject.id === session.subject_id
                            )?.name ?? "Unknown subject"}
                        </h3>
                        <p>{formatDuration(session.duration_seconds)}</p>
                        <p>{new Date(session.started_at).toLocaleString()}</p>
                    </article>
                ))}
            </div>

            <div className="history-pagination">
                <button
                    type="button"
                    disabled={data.offset === 0}
                    onClick={() =>
                        data.loadPage(Math.max(0, data.offset - data.pageSize))
                    }
                >
                    Previous
                </button>
                <button
                    type="button"
                    disabled={!data.result.has_more}
                    onClick={() =>
                        data.loadPage(data.offset + data.pageSize)
                    }
                >
                    Next
                </button>
            </div>
        </>
    );
}

function GroupedSessions({ groups }) {
    if (!groups?.length) {
        return (
            <p className="history-status">No grouped sessions found.</p>
        );
    }

    return (
        <div className="history-session-list">
            {groups.map((group) => (
                <article
                    className="history-session"
                    key={`${group.period_start}-${group.subject_id}`}
                >
                    <h3>{group.subject_name}</h3>
                    <p>
                        Period: {new Date(group.period_start).toLocaleString()}{" "}
                        – {new Date(group.period_end).toLocaleString()}
                    </p>
                    <p>Total: {formatDuration(group.duration_seconds)}</p>
                    <p>Sessions: {group.session_count}</p>
                </article>
            ))}
        </div>
    );
}

function HistorySessions({ data }) {
    return (
        <section className="history-card" aria-busy={data.loading}>
            <h2>Sessions</h2>

            {data.loading ? (
                <p className="history-status">Loading history...</p>
            ) : data.historyError ? null : data.mode ===
              HISTORY_MODES.INDIVIDUAL ? (
                <IndividualSessions data={data} />
            ) : (
                <GroupedSessions groups={data.result} />
            )}
        </section>
    );
}

export default HistorySessions;

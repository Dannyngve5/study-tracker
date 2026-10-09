function StudyTimer({ hours, minutes, seconds }) {
    return (
        <>
            <p
                className="timer"
                id="timer"
                role="timer"
                aria-label="Elapsed study time"
            >
                {String(hours).padStart(2, "0")}
                <span className="timer-separator">:</span>
                {String(minutes).padStart(2, "0")}
                <span className="timer-separator">:</span>
                {String(seconds).padStart(2, "0")}
            </p>

            <p className="timer-caption">
                Every focused minute counts.
            </p>
        </>
    );
}

export default StudyTimer;

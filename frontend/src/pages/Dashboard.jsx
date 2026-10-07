import { useEffect, useState } from "react";
import StudyTimer from "../components/StudyTimer";

const API_URL = "http://localhost:8000";

function Dashboard() {
    const [subjects, setSubjects] = useState([]);
    const [selectedSubject, setSelectedSubject] = useState(null);
    const [newSubjectName, setNewSubjectName] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadSubjects() {
            try {
                const response = await fetch(`${API_URL}/subjects`);

                if (!response.ok) {
                    throw new Error("Could not load subjects");
                }

                const data = await response.json();

                setSubjects(data);

                if (data.length > 0) {
                    setSelectedSubject(data[0]);
                }
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        }

        loadSubjects();
    }, []);

    async function handleCreateSubject(event) {
        event.preventDefault();

        const name = newSubjectName.trim();

        if (!name) {
            return;
        }

        try {
            setError("");

            const response = await fetch(`${API_URL}/subjects`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: name,
                }),
            });

            if (!response.ok) {
                if (response.status === 409) {
                    throw new Error("A subject with this name already exists.");
                }

                throw new Error("Could not create subject.");
            }

            const subject = await response.json();

            setSubjects((previous) => [...previous, subject]);
            setSelectedSubject(subject);
            setNewSubjectName("");
        } catch (error) {
            setError(error.message);
        }
    }

    if (loading) {
        return <p>Loading subjects...</p>;
    }

    return (
        <main>
            <h1>Dashboard</h1>

            {error && <p>{error}</p>}

            <form onSubmit={handleCreateSubject}>
                <input
                    type="text"
                    value={newSubjectName}
                    onChange={(event) =>
                        setNewSubjectName(event.target.value)
                    }
                    placeholder="Subject name"
                />

                <button type="submit">
                    Create subject
                </button>
            </form>

            <div>
                <label htmlFor="subject-select">
                    Subject
                </label>

                <select
                    id="subject-select"
                    value={selectedSubject?.id ?? ""}
                    onChange={(event) => {
                        const subject = subjects.find(
                            (subject) =>
                                subject.id === Number(event.target.value)
                        );

                        setSelectedSubject(subject ?? null);
                    }}
                >
                    {subjects.map((subject) => (
                        <option key={subject.id} value={subject.id}>
                            {subject.name}
                        </option>
                    ))}
                </select>
            </div>

            <StudyTimer selectedSubject={selectedSubject} />
        </main>
    );
}

export default Dashboard;
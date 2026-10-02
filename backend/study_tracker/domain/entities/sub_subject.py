from datetime import datetime


class SubSubject:

    def __init__(
        self,
        subject_id: int,
        name: str,
        id: int | None = None,
        description: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.subject_id = subject_id
        self.name = name
        self.description = description
        self.created_at = created_at

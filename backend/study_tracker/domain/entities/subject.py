from datetime import datetime


class Subject:

    def __init__(
        self,
        name: str,
        id: int | None = None,
        description: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at

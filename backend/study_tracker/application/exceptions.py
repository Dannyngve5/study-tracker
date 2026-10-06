class SubjectNotFoundError(Exception):
    def __init__(self, subject_id: int):
        super().__init__(f"Subject with id {subject_id} not found")

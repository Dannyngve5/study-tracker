class SubjectAlreadyExistsError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Subject with name '{name}' already exists")


class SubjectHasDependentsError(Exception):
    def __init__(self, subject_id: int):
        super().__init__(
            f"Subject with id {subject_id} cannot be deleted while it has related records"
        )


class SubSubjectAlreadyExistsError(Exception):
    def __init__(self, subject_id: int, name: str):
        super().__init__(
            f"SubSubject with name '{name}' already exists for subject with id {subject_id}"
        )


class SubSubjectHasDependentsError(Exception):
    def __init__(self, sub_subject_id: int):
        super().__init__(
            f"SubSubject with id {sub_subject_id} cannot be deleted while it has related records"
        )


class InvalidStudySessionStateError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

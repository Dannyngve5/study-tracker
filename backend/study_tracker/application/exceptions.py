class SubjectNotFoundError(Exception):
    def __init__(self, subject_id: int):
        super().__init__(f"Subject with id {subject_id} not found")


class StudySessionNotFoundError(Exception):
    def __init__(self, study_session_id: int):
        super().__init__(f"Study session with id {study_session_id} not found")


class StudySessionAlreadyActiveError(Exception):
    def __init__(
        self,
        subject_id: int,
        sub_subject_id: int | None = None,
    ):
        sub_subject = (
            f" and sub_subject_id {sub_subject_id}"
            if sub_subject_id is not None
            else ""
        )

        super().__init__(
            f"There is already an active study session "
            f"for subject_id {subject_id}{sub_subject}"
        )


class SubSubjectNotFoundError(Exception):
    def __init__(self, sub_subject_id: int):
        super().__init__(f"Sub-subject with id {sub_subject_id} not found")


class SubSubjectDoesNotBelongToSubjectError(Exception):
    def __init__(
        self,
        sub_subject_id: int,
        subject_id: int,
    ):
        super().__init__(
            f"Sub-subject {sub_subject_id} does not belong to subject {subject_id}"
        )

from enum import Enum


class StudySessionStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"

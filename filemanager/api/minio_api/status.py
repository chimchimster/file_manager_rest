import enum


class FileStatuses(enum.Enum):
    IN_PROGRESS = 'P'
    READY = 'R'
    ERROR = 'E'

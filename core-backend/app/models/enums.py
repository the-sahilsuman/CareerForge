from enum import StrEnum


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class ResumeStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ResumeProcessingStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class ApplicationStatus(StrEnum):
    TO_APPLY = "TO_APPLY"
    DRAFT = "DRAFT"
    APPLIED = "APPLIED"
    VIEWED = "VIEWED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    OFFER = "OFFER"
    WITHDRAWN = "WITHDRAWN"


class EmailProvider(StrEnum):
    GOOGLE = "GOOGLE"
    MICROSOFT = "MICROSOFT"


class EmailConnectionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    DISCONNECTED = "DISCONNECTED"


class EmailStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class AdminStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    DISABLED = "DISABLED"


class DatasetType(StrEnum):
    RETRIEVAL = "RETRIEVAL"
    EXTRACTION = "EXTRACTION"
    GENERATION = "GENERATION"
    AGENT = "AGENT"
    APPLICATION = "APPLICATION"


class DatasetStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class EvaluationStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BucketStatus(StrEnum):
    OPEN = "OPEN"
    DONE = "DONE"


class BucketType(StrEnum):
    TASK = "TASK"
    REMINDER = "REMINDER"
    CAREER = "CAREER"
    PERSONAL = "PERSONAL"
    CUSTOM = "CUSTOM"

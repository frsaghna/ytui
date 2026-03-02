from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

class DownloadStatus(Enum):
    PENDING = auto()
    FETCHING_FORMATS = auto()
    DOWNLOADING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

@dataclass
class Format:
    format_id: str
    extension: str
    resolution: str
    filesize: Optional[str] = None
    note: Optional[str] = None

    def __str__(self) -> str:
        res = f"[{self.format_id}] {self.extension} - {self.resolution}"
        if self.filesize:
            res += f" ({self.filesize})"
        if self.note:
            res += f" - {self.note}"
        return res

@dataclass
class DownloadJob:
    url: str
    output_path: str
    format_id: Optional[str] = None
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    formats: list[Format] = field(default_factory=list)

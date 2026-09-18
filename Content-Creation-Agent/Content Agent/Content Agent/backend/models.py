from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContentRequest:
    topic: str
    platform: str
    audience: str
    mood: str
    length: str
    goal: str


@dataclass
class ContentOption:
    id: str
    title: str
    content: str


@dataclass
class ContentSession:

    state: str = "NEW_REQUEST"

    request: Optional[ContentRequest] = None

    options: list[ContentOption] = field(default_factory=list)

    selected_option: Optional[str] = None

    current_content: Optional[str] = None

    revision_count: int = 0

    approved: bool = False
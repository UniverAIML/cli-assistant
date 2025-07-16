from typing import List, Optional, TypedDict
from datetime import datetime, timezone
import uuid
import re
import html

class NoteData(TypedDict):
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str]

TAG_REGEX = re.compile(r"^[a-z0-9-]{1,50}$")

ISO_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime(ISO_FORMAT)

def _sanitize_content(content: str) -> str:
    # Basic sanitization: escape HTML/script tags
    return html.escape(content)

class Note:
    def __init__(self, title: str, content: str = "", tags: Optional[List[str]] = None):
        self.id = str(uuid.uuid4())
        self.title = self._validate_title(title)
        self.content = self._validate_content(content)
        self.tags = self._process_tags(tags or [])
        self.created_at = _iso_now()
        self.updated_at = None

    def _validate_title(self, title: str) -> str:
        if not isinstance(title, str):
            raise ValueError("Title must be a string.")
        title = title.strip()
        if not title or len(title) < 1 or len(title) > 200:
            raise ValueError("Title must be 1-200 characters after stripping.")
        return title

    def _validate_content(self, content: str) -> str:
        if not isinstance(content, str):
            raise ValueError("Content must be a string.")
        if len(content) > 10000:
            raise ValueError("Content must be at most 10,000 characters.")
        return _sanitize_content(content)

    def _process_tags(self, tags: List[str]) -> List[str]:
        valid_tags = set()
        for tag in tags:
            tag = tag.lower()
            if not TAG_REGEX.match(tag):
                continue
            valid_tags.add(tag)
        return sorted(valid_tags)

    def update_content(self, content: str) -> None:
        self.content = self._validate_content(content)
        self.updated_at = _iso_now()

    def update_title(self, title: str) -> None:
        self.title = self._validate_title(title)
        self.updated_at = _iso_now()

    def add_tag(self, tag: str) -> bool:
        tag = tag.lower()
        if not TAG_REGEX.match(tag):
            return False
        if tag in self.tags:
            return False
        self.tags.append(tag)
        self.tags = sorted(set(self.tags))
        self.updated_at = _iso_now()
        return True

    def remove_tag(self, tag: str) -> bool:
        tag = tag.lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = _iso_now()
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        tag = tag.lower()
        return tag in self.tags

    def get_tags(self) -> List[str]:
        return sorted(self.tags)

    def search_in_content(self, query: str) -> bool:
        query = query.lower()
        return query in self.title.lower() or query in self.content.lower()

    def matches_tags(self, tag_list: List[str]) -> bool:
        tag_set = set(t.lower() for t in tag_list)
        return any(tag in tag_set for tag in self.tags)

    def get_search_score(self, query: str) -> float:
        query = query.lower()
        score = 0.0
        if query in self.title.lower():
            score += 2.0
        if query in self.content.lower():
            score += 1.0
        if any(query == tag for tag in self.tags):
            score += 1.5
        return score

    def to_typed_dict(self) -> NoteData:
        return NoteData(
            id=self.id,
            title=self.title,
            content=self.content,
            tags=self.get_tags(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_typed_dict(cls, data: NoteData) -> 'Note':
        note = cls(
            title=data['title'],
            content=data.get('content', ""),
            tags=data.get('tags', [])
        )
        note.id = data['id']
        note.created_at = data['created_at']
        note.updated_at = data.get('updated_at')
        return note

    def __str__(self) -> str:
        tags_str = ', '.join(self.get_tags())
        content_preview = self.content[:100] + ('...' if len(self.content) > 100 else '')
        return f"Note(title='{self.title}', created_at='{self.created_at}', tags=[{tags_str}], content='{content_preview}')"
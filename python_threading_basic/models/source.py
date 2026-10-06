"""
Model đại diện cho Nguồn tin tức (Source)
"""
from typing import Optional, Dict, Any

class Source:
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        url: str = "",
        is_active: bool = True,
        article_list_selector: str = "",
        title_selector: str = "",
        description_selector: str = "",
        content_selector: str = "",
        author_selector: str = "",
        published_date_selector: str = "",
        created_at: Optional[Any] = None,
        updated_at: Optional[Any] = None
    ):
        self.id = id
        self.name = name
        self.url = url
        self.is_active = bool(is_active)
        self.article_list_selector = article_list_selector or ""
        self.title_selector = title_selector or ""
        self.description_selector = description_selector or ""
        self.content_selector = content_selector or ""
        self.author_selector = author_selector or ""
        self.published_date_selector = published_date_selector or ""
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_row(cls, row: tuple) -> "Source":
        """Khởi tạo đối tượng Source từ 1 dòng dữ liệu MySQL cursor"""
        return cls(
            id=row[0],
            name=row[1],
            url=row[2],
            is_active=bool(row[3]),
            article_list_selector=row[4] if len(row) > 4 else "",
            title_selector=row[5] if len(row) > 5 else "",
            description_selector=row[6] if len(row) > 6 else "",
            content_selector=row[7] if len(row) > 7 else "",
            author_selector=row[8] if len(row) > 8 else "",
            published_date_selector=row[9] if len(row) > 9 else "",
            created_at=row[10] if len(row) > 10 else None,
            updated_at=row[11] if len(row) > 11 else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển thành từ điển key-value"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "is_active": self.is_active,
            "article_list_selector": self.article_list_selector,
            "title_selector": self.title_selector,
            "description_selector": self.description_selector,
            "content_selector": self.content_selector,
            "author_selector": self.author_selector,
            "published_date_selector": self.published_date_selector,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }

    def __str__(self) -> str:
        status_text = "Hoạt động (Active)" if self.is_active else "Tắt (Inactive)"
        return f"Source [#{self.id}] {self.name} - {self.url} ({status_text})"

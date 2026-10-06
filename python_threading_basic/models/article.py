"""
Model đại diện cho Bài viết tin tức (Article)
"""
from typing import Optional, Dict, Any

class Article:
    def __init__(
        self,
        id: Optional[int] = None,
        source_id: int = 0,
        url: str = "",
        title: str = "",
        summary: Optional[str] = "",
        content: Optional[str] = "",
        author: Optional[str] = "",
        published_date: Optional[str] = "",
        thumbnail_url: Optional[str] = "",
        crawled_at: Optional[Any] = None,
        status: str = "COMPLETED",
        source_name: Optional[str] = ""
    ):
        self.id = id
        self.source_id = source_id
        self.url = url
        self.title = title
        self.summary = summary or ""
        self.content = content or ""
        self.author = author or ""
        self.published_date = published_date or ""
        self.thumbnail_url = thumbnail_url or ""
        self.crawled_at = crawled_at
        self.status = status or "COMPLETED"
        self.source_name = source_name or ""

    @classmethod
    def from_row(cls, row: tuple) -> "Article":
        """
        Khởi tạo Article từ dòng dữ liệu MySQL.
        Hỗ trợ cả trường hợp SELECT * từ articles lẫn SELECT kèm source_name qua JOIN.
        """
        source_name = row[11] if len(row) > 11 else ""
        return cls(
            id=row[0],
            source_id=row[1],
            url=row[2],
            title=row[3],
            summary=row[4],
            content=row[5],
            author=row[6],
            published_date=row[7],
            thumbnail_url=row[8],
            crawled_at=row[9],
            status=row[10] if len(row) > 10 else "COMPLETED",
            source_name=source_name
        )

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển thành từ điển dữ liệu"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "url": self.url,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "author": self.author,
            "published_date": self.published_date,
            "thumbnail_url": self.thumbnail_url,
            "crawled_at": str(self.crawled_at) if self.crawled_at else None,
            "status": self.status
        }

    def __str__(self) -> str:
        return f"Article [#{self.id}] {self.title} - ({self.source_name or self.source_id})"
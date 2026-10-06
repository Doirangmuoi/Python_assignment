"""
Repository phụ trách thao tác CSDL cho Bài viết tin tức (Article)
"""
from typing import List, Optional, Tuple, Dict, Any
import mysql.connector
from database.db_connection import DatabaseConnection
from models.article import Article

class ArticleRepository:
    def save(self, article: Article) -> Tuple[bool, bool]:
        """
        Lưu hoặc cập nhật bài viết vào CSDL (xử lý chống trùng lặp theo URL).
        Trả về Tuple (thành_công, là_bài_mới):
        - (True, True): Cào và thêm mới thành công bài viết.
        - (True, False): Bài viết đã tồn tại trong DB, được cập nhật nội dung.
        - (False, False): Lỗi khi lưu.
        """
        query = """
            INSERT INTO articles (
                source_id, url, title, summary, content, 
                author, published_date, thumbnail_url, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                summary = VALUES(summary),
                content = VALUES(content),
                author = VALUES(author),
                published_date = VALUES(published_date),
                thumbnail_url = VALUES(thumbnail_url),
                status = VALUES(status)
        """
        params = (
            article.source_id,
            article.url,
            article.title,
            article.summary,
            article.content,
            article.author,
            article.published_date,
            article.thumbnail_url,
            article.status
        )
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # Trong MySQL, nếu INSERT thành công rowcount = 1, nếu UPDATE rowcount = 2, nếu không đổi rowcount = 0
            is_new = (cursor.rowcount == 1)
            cursor.close()
            return True, is_new
        except mysql.connector.Error as e:
            print(f"[LỖI LƯU BÀI VIẾT] {e}")
            return False, False
        finally:
            conn.close()

    def url_exists(self, url: str) -> bool:
        """Kiểm tra đường dẫn URL đã được cào trong hệ thống hay chưa"""
        query = "SELECT id FROM articles WHERE url = %s LIMIT 1"
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (url,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        finally:
            conn.close()

    def get_by_id(self, article_id: int) -> Optional[Article]:
        """Lấy chi tiết một bài viết theo ID kèm tên nguồn tin"""
        query = """
            SELECT 
                a.id, a.source_id, a.url, a.title, a.summary, a.content,
                a.author, a.published_date, a.thumbnail_url, a.crawled_at, 
                a.status, s.name as source_name
            FROM articles a
            LEFT JOIN sources s ON a.source_id = s.id
            WHERE a.id = %s
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (article_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return Article.from_row(row)
            return None
        finally:
            conn.close()

    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 8,
        search_keyword: Optional[str] = None,
        source_id: Optional[int] = None,
        crawl_date: Optional[str] = None
    ) -> List[Article]:
        """
        Lấy danh sách bài viết phân trang kèm bộ lọc và tìm kiếm
        """
        offset = (page - 1) * page_size
        where_clauses, params = self._build_where_clause(search_keyword, source_id, crawl_date)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = f"""
            SELECT 
                a.id, a.source_id, a.url, a.title, a.summary, a.content,
                a.author, a.published_date, a.thumbnail_url, a.crawled_at, 
                a.status, s.name as source_name
            FROM articles a
            LEFT JOIN sources s ON a.source_id = s.id
            {where_sql}
            ORDER BY a.crawled_at DESC, a.id DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])

        articles = []
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                articles.append(Article.from_row(row))
            cursor.close()
        finally:
            conn.close()
        return articles

    def count_articles(
        self,
        search_keyword: Optional[str] = None,
        source_id: Optional[int] = None,
        crawl_date: Optional[str] = None
    ) -> int:
        """Đếm tổng số bài viết thỏa mãn điều kiện lọc/tìm kiếm"""
        where_clauses, params = self._build_where_clause(search_keyword, source_id, crawl_date)
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = f"SELECT COUNT(*) FROM articles a {where_sql}"

        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            total = cursor.fetchone()[0]
            cursor.close()
            return total
        finally:
            conn.close()

    def _build_where_clause(
        self,
        search_keyword: Optional[str] = None,
        source_id: Optional[int] = None,
        crawl_date: Optional[str] = None
    ) -> Tuple[List[str], List[Any]]:
        """Xây dựng mệnh đề WHERE động cho câu lệnh tìm kiếm/lọc bài viết"""
        where_clauses = []
        params = []

        if search_keyword and search_keyword.strip():
            kw = f"%{search_keyword.strip()}%"
            where_clauses.append("(a.title LIKE %s OR a.summary LIKE %s OR a.content LIKE %s)")
            params.extend([kw, kw, kw])

        if source_id:
            where_clauses.append("a.source_id = %s")
            params.append(source_id)

        if crawl_date and crawl_date.strip():
            where_clauses.append("DATE(a.crawled_at) = %s")
            params.append(crawl_date.strip())

        return where_clauses, params

    def delete_by_id(self, article_id: int) -> bool:
        """Xóa bài viết theo ID"""
        query = "DELETE FROM articles WHERE id = %s"
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (article_id,))
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        finally:
            conn.close()

    def delete_older_than(self, days: int) -> int:
        """Xóa các bài viết cũ hơn số ngày chỉ định (dựa trên crawled_at)"""
        query = "DELETE FROM articles WHERE crawled_at < NOW() - INTERVAL %s DAY"
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (days,))
            deleted_count = cursor.rowcount
            cursor.close()
            return deleted_count
        finally:
            conn.close()

    def delete_duplicates(self) -> int:
        """
        Dọn dẹp bài viết trùng tiêu đề hoặc URL nếu có (giữ lại bài có ID nhỏ nhất)
        """
        query = """
            DELETE a1 FROM articles a1
            INNER JOIN articles a2 
            WHERE a1.id > a2.id AND a1.url = a2.url
        """
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            deleted_count = cursor.rowcount
            cursor.close()
            return deleted_count
        finally:
            conn.close()

    def get_all_for_export(
        self,
        source_id: Optional[int] = None,
        crawl_date: Optional[str] = None
    ) -> List[Article]:
        """Lấy tất cả bài viết phục vụ xuất file báo cáo (CSV/Excel/JSON)"""
        where_clauses, params = self._build_where_clause(None, source_id, crawl_date)
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = f"""
            SELECT 
                a.id, a.source_id, a.url, a.title, a.summary, a.content,
                a.author, a.published_date, a.thumbnail_url, a.crawled_at, 
                a.status, s.name as source_name
            FROM articles a
            LEFT JOIN sources s ON a.source_id = s.id
            {where_sql}
            ORDER BY a.id ASC
        """
        articles = []
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                articles.append(Article.from_row(row))
            cursor.close()
        finally:
            conn.close()
        return articles

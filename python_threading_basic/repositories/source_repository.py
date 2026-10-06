"""
Repository phụ trách thao tác CSDL cho Nguồn tin (Source)
"""
from typing import List, Optional
import mysql.connector
from database.db_connection import DatabaseConnection
from models.source import Source

class SourceRepository:
    def get_all(self, active_only: bool = False) -> List[Source]:
        """Lấy tất cả các nguồn tin tức trong CSDL"""
        query = "SELECT id, name, url, is_active, article_list_selector, title_selector, description_selector, content_selector, author_selector, published_date_selector, created_at, updated_at FROM sources"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id ASC"

        sources = []
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                sources.append(Source.from_row(row))
            cursor.close()
        finally:
            conn.close()
        return sources

    def get_by_id(self, source_id: int) -> Optional[Source]:
        """Lấy thông tin nguồn tin theo ID"""
        query = "SELECT id, name, url, is_active, article_list_selector, title_selector, description_selector, content_selector, author_selector, published_date_selector, created_at, updated_at FROM sources WHERE id = %s"
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (source_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return Source.from_row(row)
            return None
        finally:
            conn.close()

    def add(self, source: Source) -> int:
        """Thêm một nguồn tin mới vào CSDL"""
        query = """
            INSERT INTO sources (
                name, url, is_active, 
                article_list_selector, title_selector, 
                description_selector, content_selector, 
                author_selector, published_date_selector
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            source.name,
            source.url,
            1 if source.is_active else 0,
            source.article_list_selector,
            source.title_selector,
            source.description_selector,
            source.content_selector,
            source.author_selector,
            source.published_date_selector
        )
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            new_id = cursor.lastrowid
            cursor.close()
            return new_id
        finally:
            conn.close()

    def update(self, source: Source) -> bool:
        """Cập nhật thông tin nguồn tin theo ID"""
        query = """
            UPDATE sources SET
                name = %s,
                url = %s,
                is_active = %s,
                article_list_selector = %s,
                title_selector = %s,
                description_selector = %s,
                content_selector = %s,
                author_selector = %s,
                published_date_selector = %s
            WHERE id = %s
        """
        params = (
            source.name,
            source.url,
            1 if source.is_active else 0,
            source.article_list_selector,
            source.title_selector,
            source.description_selector,
            source.content_selector,
            source.author_selector,
            source.published_date_selector,
            source.id
        )
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        finally:
            conn.close()

    def delete(self, source_id: int) -> bool:
        """Xóa nguồn tin khỏi CSDL theo ID (các bài viết liên quan sẽ bị xóa tự động theo CASCADE)"""
        query = "DELETE FROM sources WHERE id = %s"
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (source_id,))
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        finally:
            conn.close()

    def toggle_active(self, source_id: int) -> Optional[bool]:
        """Đảo trạng thái kích hoạt (Active <-> Inactive) của nguồn tin"""
        source = self.get_by_id(source_id)
        if not source:
            return None
        new_status = not source.is_active
        query = "UPDATE sources SET is_active = %s WHERE id = %s"
        conn = DatabaseConnection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (1 if new_status else 0, source_id))
            cursor.close()
            return new_status
        finally:
            conn.close()

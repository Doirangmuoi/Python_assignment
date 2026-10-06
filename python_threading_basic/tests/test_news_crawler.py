"""
Bộ kiểm thử tự động cho hệ thống News Crawler
Chạy bằng lệnh: python -m unittest tests/test_news_crawler.py
"""
import unittest
import os
import sys

# Đảm bảo UTF-8 cho Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Đảm bảo import được các module từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import DatabaseConnection
from repositories.source_repository import SourceRepository
from repositories.article_repository import ArticleRepository
from services.crawler_factory import CrawlerFactory
from services.export_service import ExportService
from services.scheduler_service import SchedulerService

class TestNewsCrawlerSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Đảm bảo database đã được khởi tạo
        cls.db_ok = DatabaseConnection.init_database()
        cls.source_repo = SourceRepository()
        cls.article_repo = ArticleRepository()

    def test_01_database_connection(self):
        self.assertTrue(self.db_ok, "Kết nối và khởi tạo CSDL MySQL thất bại")

    def test_02_sources_seeded(self):
        sources = self.source_repo.get_all()
        self.assertGreaterEqual(len(sources), 3, "Phải có ít nhất 3 nguồn tin tức trong DB")
        names = [s.name for s in sources]
        self.assertIn("VnExpress", names)
        self.assertIn("Dân Trí", names)
        self.assertIn("Tuổi Trẻ", names)

    def test_03_crawler_factory_and_crawl(self):
        sources = self.source_repo.get_all(active_only=True)
        self.assertTrue(len(sources) > 0)
        sample_source = sources[0]
        crawler = CrawlerFactory.get_crawler(sample_source)
        self.assertIsNotNone(crawler)

        # Cào thử 2 bài viết
        result = crawler.crawl_source(sample_source, self.article_repo, max_articles=2, max_workers=2)
        self.assertIn("scanned", result)
        self.assertIn("new", result)
        self.assertGreater(result["scanned"], 0)

    def test_04_article_queries_and_pagination(self):
        total = self.article_repo.count_articles()
        self.assertGreater(total, 0, "Phải có bài viết trong CSDL")

        page_articles = self.article_repo.get_paginated(page=1, page_size=5)
        self.assertLessEqual(len(page_articles), 5)
        self.assertGreater(len(page_articles), 0)

        # Kiểm tra chi tiết bài viết
        first_id = page_articles[0].id
        detail = self.article_repo.get_by_id(first_id)
        self.assertIsNotNone(detail)
        self.assertEqual(detail.id, first_id)
        self.assertTrue(len(detail.title) > 0)

    def test_05_export_services(self):
        articles = self.article_repo.get_all_for_export()
        self.assertGreater(len(articles), 0)

        f_csv = ExportService.export_to_csv(articles)
        self.assertTrue(os.path.exists(f_csv))

        f_xlsx = ExportService.export_to_excel(articles)
        self.assertTrue(os.path.exists(f_xlsx))

        f_json = ExportService.export_to_json(articles)
        self.assertTrue(os.path.exists(f_json))

    def test_06_scheduler_lifecycle(self):
        sched = SchedulerService()
        self.assertFalse(sched.is_running)

        started = sched.start(interval_minutes=20)
        self.assertTrue(started)
        self.assertTrue(sched.is_running)

        status = sched.get_status()
        self.assertEqual(status["interval_minutes"], 20)

        stopped = sched.stop()
        self.assertTrue(stopped)
        self.assertFalse(sched.is_running)

if __name__ == "__main__":
    unittest.main()

"""
Cấu hình hệ thống News Crawler
"""
import os
import sys

# Đảm bảo Terminal Windows in tiếng Việt UTF-8 không bao giờ bị lỗi charmap encode
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Cấu hình CSDL MySQL
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "news_crawler_db")

# Cấu hình Crawler
DEFAULT_REQUEST_TIMEOUT = 12
DEFAULT_MAX_WORKERS = 6  # Số luồng multithreading cào bài viết
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Cấu hình phân trang hiển thị bài viết
DEFAULT_PAGE_SIZE = 8

# Thư mục xuất file báo cáo
EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

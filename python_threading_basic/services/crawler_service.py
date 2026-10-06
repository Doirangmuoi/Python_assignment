"""
Interface trừu tượng cơ sở cho các Crawler Service.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from models.source import Source
from models.article import Article
import config

class CrawlerService(ABC):
    def __init__(self, timeout: int = config.DEFAULT_REQUEST_TIMEOUT):
        self.timeout = timeout
        self.headers = {
            "User-Agent": config.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    @abstractmethod
    def crawl_fresh_link(self, source: Source, max_articles: int = 20) -> List[str]:
        """
        Lấy danh sách các đường dẫn bài viết mới từ trang chủ/chuyên mục.
        :param source: Đối tượng nguồn tin
        :param max_articles: Giới hạn số lượng link cần lấy
        :return: Danh sách các URL bài viết duy nhất
        """
        pass

    @abstractmethod
    def crawl_link_detail(self, url: str, source: Source) -> Optional[Article]:
        """
        Cào thông tin chi tiết của một bài viết: Tiêu đề, Tóm tắt, Nội dung, Tác giả, Ngày đăng, Ảnh...
        :param url: Đường dẫn chi tiết bài viết
        :param source: Nguồn tin chứa cấu hình selector
        :return: Đối tượng Article hoặc None nếu cào thất bại
        """
        pass

    def crawl_source(
        self, 
        source: Source, 
        article_repository, 
        max_articles: int = 15,
        max_workers: int = config.DEFAULT_MAX_WORKERS
    ) -> Dict[str, Any]:
        """
        Quy trình chuẩn cào toàn bộ 1 nguồn tin áp dụng Multithreading.
        1. Quét danh sách link bài viết mới.
        2. Dùng ThreadPoolExecutor cào đồng thời nhiều bài viết để tăng tốc.
        3. Lưu vào Database và kiểm tra chống trùng lặp.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time

        print(f"\n[*] Bắt đầu cào dữ liệu từ nguồn: [{source.name}] ({source.url})")
        start_time = time.time()

        # Bước 1: Lấy danh sách liên kết
        links = self.crawl_fresh_link(source, max_articles=max_articles)
        print(f"[{source.name}] Tìm thấy {len(links)} liên kết bài viết.")
        if not links:
            print(f"[{source.name}] Không tìm thấy bài viết nào hoặc không thể kết nối.")
            return {"scanned": 0, "new": 0, "updated": 0, "failed": 0, "duration": 0}

        new_count = 0
        updated_count = 0
        failed_count = 0
        total_scanned = len(links)

        # Bước 2: Cào chi tiết đa luồng (Multithreading)
        print(f"[{source.name}] Đang cào chi tiết với {max_workers} luồng (Multithreading)...")

        def _worker(target_url: str):
            try:
                article = self.crawl_link_detail(target_url, source)
                if article:
                    success, is_new = article_repository.save(article)
                    return {"success": success, "is_new": is_new, "article": article, "url": target_url}
                else:
                    return {"success": False, "is_new": False, "article": None, "url": target_url}
            except Exception as ex:
                return {"success": False, "is_new": False, "error": str(ex), "url": target_url}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(_worker, url): url for url in links}
            completed_index = 0

            for future in as_completed(future_to_url):
                completed_index += 1
                res = future.result()
                if res.get("success"):
                    art = res.get("article")
                    if res.get("is_new"):
                        new_count += 1
                        print(f"  [{completed_index}/{total_scanned}] [+] Mới: {art.title[:65]}...")
                    else:
                        updated_count += 1
                        print(f"  [{completed_index}/{total_scanned}] [~] Cập nhật: {art.title[:65]}...")
                else:
                    failed_count += 1
                    err_msg = res.get("error", "Bóc tách dữ liệu rỗng")
                    print(f"  [{completed_index}/{total_scanned}] [-] Thất bại ({err_msg}): {res.get('url')[:60]}...")

        duration = round(time.time() - start_time, 2)
        print(f"\n=> [{source.name}] Hoàn thành trong {duration}s! Thêm mới: {new_count} | Cập nhật: {updated_count} | Thất bại: {failed_count}\n")
        return {
            "scanned": total_scanned,
            "new": new_count,
            "updated": updated_count,
            "failed": failed_count,
            "duration": duration
        }
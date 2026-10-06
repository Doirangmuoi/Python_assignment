"""
Factory tạo CrawlerService phù hợp với từng Nguồn tin (Crawler Factory Pattern)
"""
from models.source import Source
from services.crawler_service import CrawlerService
from services.vnexpress_crawler_service import VnexpressCrawlerService
from services.dantri_crawler_service import DantriCrawlerService
from services.tuoitre_crawler_service import TuoitreCrawlerService
from services.muong14_crawler_service import Muong14CrawlerService
from services.general_crawler_service import GeneralCrawlerService

class CrawlerFactory:
    @staticmethod
    def get_crawler(source: Source) -> CrawlerService:
        """
        Trả về Crawler chuyên biệt theo tên/URL nguồn, hoặc Crawler tổng quát nếu là nguồn mới
        """
        source_name = (source.name or "").lower()
        source_url = (source.url or "").lower()

        if "vnexpress" in source_name or "vnexpress.net" in source_url:
            return VnexpressCrawlerService()
        elif "dân trí" in source_name or "dantri" in source_name or "dantri.com.vn" in source_url:
            return DantriCrawlerService()
        elif "tuổi trẻ" in source_name or "tuoitre" in source_name or "tuoitre.vn" in source_url:
            return TuoitreCrawlerService()
        elif "kênh 14" in source_name or "mương 14" in source_name or "kenh14.vn" in source_url:
            return Muong14CrawlerService()
        else:
            return GeneralCrawlerService()

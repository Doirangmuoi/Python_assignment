"""
Crawler chuyên biệt cho báo Tuổi Trẻ (tuoitre.vn)
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from models.source import Source
from models.article import Article
from services.crawler_service import CrawlerService

class TuoitreCrawlerService(CrawlerService):
    def crawl_fresh_link(self, source: Source, max_articles: int = 20) -> List[str]:
        target_url = source.url or "https://tuoitre.vn/thoi-su.htm"
        links = []
        try:
            response = requests.get(target_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            seen = set()
            # Tìm tất cả thẻ a có href đuôi .htm và có chứa ID bài viết
            for a_tag in soup.find_all("a"):
                href = a_tag.get("href", "").strip().split("#")[0]
                if not href:
                    continue
                if not href.startswith("http"):
                    href = "https://tuoitre.vn" + href

                # Link bài viết thường có dạng: -<id_so>.htm
                if href.endswith(".htm") and "-" in href and href not in seen:
                    # Lọc bỏ các trang chuyên mục hoặc video
                    if not any(x in href for x in ["/video", "/media", "/chuyen-muc", "can-biet.htm"]):
                        # Kiểm tra xem có đuôi số bài viết không
                        part = href.split("-")[-1].replace(".htm", "")
                        if part.isdigit() and len(part) >= 6:
                            seen.add(href)
                            links.append(href)
                            if len(links) >= max_articles:
                                break

        except requests.RequestException as e:
            print(f"[Tuổi Trẻ - Lỗi mạng] Không thể tải danh sách bài: {e}")
        except Exception as e:
            print(f"[Tuổi Trẻ - Lỗi bóc tách link] {e}")

        return links

    def crawl_link_detail(self, url: str, source: Source) -> Optional[Article]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Tiêu đề
            title_el = (
                soup.select_one(source.title_selector or "h1.detail-title") 
                or soup.select_one("h1.article-title") 
                or soup.find("h1")
            )
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                return None

            # 2. Tóm tắt (Sapo)
            desc_el = (
                soup.select_one(source.description_selector or "h2.detail-sapo") 
                or soup.select_one("h2.article-sapo")
            )
            summary = desc_el.get_text(strip=True) if desc_el else ""

            # 3. Nội dung bài viết
            body_el = soup.select_one(source.content_selector or "div.detail-content") or soup.select_one("div.article-content")
            paras = []
            if body_el:
                for p in body_el.find_all("p"):
                    if p.find_parent("figure") or p.find_parent(".box-related"):
                        continue
                    text = p.get_text(strip=True)
                    if text:
                        paras.append(text)
            content = "\n\n".join(paras)

            # 4. Ngày đăng
            date_el = soup.select_one(source.published_date_selector or "div.detail-time") or soup.select_one("div.article-date")
            published_date = date_el.get_text(strip=True) if date_el else ""

            # 5. Tác giả
            author_el = soup.select_one(source.author_selector or "div.author-info") or soup.select_one(".detail-author")
            author = author_el.get_text(strip=True) if author_el else ""

            # 6. Ảnh đại diện
            thumb_el = soup.select_one('meta[property="og:image"]')
            thumbnail_url = thumb_el.get("content", "") if thumb_el else ""

            return Article(
                source_id=source.id or 3,
                source_name=source.name,
                url=url,
                title=title,
                summary=summary,
                content=content,
                author=author,
                published_date=published_date,
                thumbnail_url=thumbnail_url,
                status="COMPLETED"
            )

        except requests.RequestException as e:
            print(f"[Tuổi Trẻ - Lỗi tải bài] {url}: {e}")
            return None
        except Exception as e:
            print(f"[Tuổi Trẻ - Lỗi phân tích bài] {url}: {e}")
            return None

"""
Crawler chuyên biệt cho báo VnExpress (vnexpress.net)
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from models.source import Source
from models.article import Article
from services.crawler_service import CrawlerService

class VnexpressCrawlerService(CrawlerService):
    def crawl_fresh_link(self, source: Source, max_articles: int = 20) -> List[str]:
        target_url = source.url or "https://vnexpress.net/thoi-su"
        links = []
        try:
            response = requests.get(target_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            selector = source.article_list_selector or "article.item-news h3.title-news a, h3.title-news a"
            seen = set()

            for a_tag in soup.select(selector):
                href = a_tag.get("href", "").strip().split("#")[0]
                if href and href.startswith("https://vnexpress.net/") and href.endswith(".html"):
                    if href not in seen and not any(x in href for x in ["/video/", "/interactive/", "/podcast/"]):
                        seen.add(href)
                        links.append(href)
                        if len(links) >= max_articles:
                            break

        except requests.RequestException as e:
            print(f"[VnExpress - Lỗi mạng] Không thể tải danh sách bài: {e}")
        except Exception as e:
            print(f"[VnExpress - Lỗi bóc tách link] {e}")

        return links

    def crawl_link_detail(self, url: str, source: Source) -> Optional[Article]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Tiêu đề
            title_el = soup.select_one(source.title_selector or "h1.title-detail") or soup.find("h1")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                return None

            # 2. Tóm tắt (Sapo)
            desc_el = soup.select_one(source.description_selector or "p.description")
            summary = desc_el.get_text(strip=True) if desc_el else ""

            # 3. Nội dung bài viết
            content_el = soup.select_one(source.content_selector or "article.fck_detail")
            paragraphs = []
            if content_el:
                for p in content_el.select("p.Normal"):
                    p_text = p.get_text(strip=True)
                    if p_text:
                        paragraphs.append(p_text)
                if not paragraphs:
                    paragraphs = [p.get_text(strip=True) for p in content_el.find_all("p") if p.get_text(strip=True)]
            content = "\n\n".join(paragraphs)

            # 4. Ngày xuất bản
            date_el = soup.select_one(source.published_date_selector or "span.date")
            published_date = date_el.get_text(strip=True) if date_el else ""

            # 5. Tác giả
            author_el = soup.select_one(source.author_selector or "p.author_mail, p.Normal strong")
            author = author_el.get_text(strip=True) if author_el else ""

            # 6. Ảnh đại diện
            thumb_el = soup.select_one('meta[property="og:image"]')
            thumbnail_url = thumb_el.get("content", "") if thumb_el else ""

            return Article(
                source_id=source.id or 1,
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
            print(f"[VnExpress - Lỗi tải bài] {url}: {e}")
            return None
        except Exception as e:
            print(f"[VnExpress - Lỗi phân tích bài] {url}: {e}")
            return None

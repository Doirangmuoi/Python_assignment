"""
Crawler chuyên biệt cho báo Dân Trí (dantri.com.vn)
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from models.source import Source
from models.article import Article
from services.crawler_service import CrawlerService

class DantriCrawlerService(CrawlerService):
    def crawl_fresh_link(self, source: Source, max_articles: int = 20) -> List[str]:
        target_url = source.url or "https://dantri.com.vn/xa-hoi.htm"
        links = []
        try:
            response = requests.get(target_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            selector = source.article_list_selector or "article.article-item h3.article-title a, h3.article-title a"
            seen = set()

            for a_tag in soup.select(selector):
                href = a_tag.get("href", "").strip().split("#")[0]
                if not href:
                    continue
                if not href.startswith("http"):
                    href = "https://dantri.com.vn" + href

                if href.endswith(".htm") and href not in seen:
                    if not any(x in href for x in ["/video/", "/photo/"]):
                        seen.add(href)
                        links.append(href)
                        if len(links) >= max_articles:
                            break

        except requests.RequestException as e:
            print(f"[Dân Trí - Lỗi mạng] Không thể tải danh sách bài: {e}")
        except Exception as e:
            print(f"[Dân Trí - Lỗi bóc tách link] {e}")

        return links

    def crawl_link_detail(self, url: str, source: Source) -> Optional[Article]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")

            article_tag = soup.find("article") or soup

            # 1. Tiêu đề
            title_el = article_tag.find("h1") or soup.find("h1")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                return None

            # 2. Tóm tắt (Sapo)
            desc_el = article_tag.find("h2") or soup.select_one(".singular-sapo")
            summary = desc_el.get_text(strip=True) if desc_el else ""

            # 3. Nội dung bài viết
            body_el = soup.select_one(".singular-content") or article_tag
            paras = []
            if body_el:
                for p in body_el.find_all("p"):
                    # Bỏ qua các đoạn chú thích ảnh hoặc quảng cáo
                    if p.find_parent("figure") or "image" in " ".join(p.get("class", [])):
                        continue
                    text = p.get_text(strip=True)
                    if text:
                        paras.append(text)
            content = "\n\n".join(paras)

            # 4. Ngày đăng
            date_el = soup.select_one("time.author-time") or soup.select_one(".author-time") or soup.find("time")
            published_date = date_el.get_text(strip=True) if date_el else ""

            # 5. Tác giả
            author_el = soup.select_one(".author-name") or soup.select_one("article p strong")
            author = author_el.get_text(strip=True) if author_el else ""

            # 6. Ảnh đại diện
            thumb_el = soup.select_one('meta[property="og:image"]')
            thumbnail_url = thumb_el.get("content", "") if thumb_el else ""

            return Article(
                source_id=source.id or 2,
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
            print(f"[Dân Trí - Lỗi tải bài] {url}: {e}")
            return None
        except Exception as e:
            print(f"[Dân Trí - Lỗi phân tích bài] {url}: {e}")
            return None
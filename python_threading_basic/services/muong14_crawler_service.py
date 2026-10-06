"""
Crawler cho trang Kênh 14 / Mương 14 (kenh14.vn)
"""
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from models.source import Source
from models.article import Article
from services.crawler_service import CrawlerService

class Muong14CrawlerService(CrawlerService):
    def crawl_fresh_link(self, source: Source, max_articles: int = 20) -> List[str]:
        target_url = source.url or "https://kenh14.vn/xa-hoi.chn"
        links = []
        try:
            response = requests.get(target_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            seen = set()
            for a_tag in soup.select("h3.knswli-title a, a[href$='.chn']"):
                href = a_tag.get("href", "").strip().split("#")[0]
                if not href:
                    continue
                if not href.startswith("http"):
                    href = "https://kenh14.vn" + href

                if href.endswith(".chn") and href not in seen and not any(x in href for x in ["/video", "/tv"]):
                    seen.add(href)
                    links.append(href)
                    if len(links) >= max_articles:
                        break

        except requests.RequestException as e:
            print(f"[Kênh 14 - Lỗi mạng] Không thể tải danh sách: {e}")
        except Exception as e:
            print(f"[Kênh 14 - Lỗi link] {e}")

        return links

    def crawl_link_detail(self, url: str, source: Source) -> Optional[Article]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")

            title_el = soup.select_one("h1.kbwc-title") or soup.find("h1")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                return None

            desc_el = soup.select_one("h2.knc-sapo") or soup.find("h2")
            summary = desc_el.get_text(strip=True) if desc_el else ""

            body_el = soup.select_one("div.knc-content")
            paras = []
            if body_el:
                for p in body_el.find_all("p"):
                    t = p.get_text(strip=True)
                    if t:
                        paras.append(t)
            content = "\n\n".join(paras)

            date_el = soup.select_one("span.kbwcm-time")
            published_date = date_el.get_text(strip=True) if date_el else ""

            author_el = soup.select_one("span.kbwcm-author")
            author = author_el.get_text(strip=True) if author_el else ""

            thumb_el = soup.select_one('meta[property="og:image"]')
            thumbnail_url = thumb_el.get("content", "") if thumb_el else ""

            return Article(
                source_id=source.id or 4,
                source_name=source.name or "Kênh 14",
                url=url,
                title=title,
                summary=summary,
                content=content,
                author=author,
                published_date=published_date,
                thumbnail_url=thumbnail_url,
                status="COMPLETED"
            )

        except Exception as e:
            print(f"[Kênh 14 - Lỗi tải bài] {url}: {e}")
            return None
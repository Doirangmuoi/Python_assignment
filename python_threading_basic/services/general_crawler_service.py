"""
Crawler tổng quát dựa trên cấu hình CSS Selectors của Nguồn tin trong DB.
Cho phép cào bất kỳ website nào mà người dùng thêm mới vào hệ thống.
"""
from typing import List, Optional
import urllib.parse
import requests
from bs4 import BeautifulSoup
from models.source import Source
from models.article import Article
from services.crawler_service import CrawlerService

class GeneralCrawlerService(CrawlerService):
    def crawl_fresh_link(self, source: Source, max_articles: int = 20) -> List[str]:
        target_url = source.url
        links = []
        if not target_url:
            return links

        try:
            response = requests.get(target_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            selector = source.article_list_selector or "a"
            seen = set()

            for a_tag in soup.select(selector):
                href = a_tag.get("href", "").strip().split("#")[0]
                if not href:
                    continue

                # Chuẩn hóa URL tuyệt đối
                full_url = urllib.parse.urljoin(target_url, href)

                # Bỏ qua link không hợp lệ hoặc trùng lặp
                if full_url.startswith("http") and full_url not in seen:
                    # Kiểm tra tránh lấy lại chính URL trang chủ
                    if full_url.rstrip("/") != target_url.rstrip("/"):
                        seen.add(full_url)
                        links.append(full_url)
                        if len(links) >= max_articles:
                            break

        except requests.RequestException as e:
            print(f"[{source.name} - Lỗi mạng] Không thể tải danh sách bài: {e}")
        except Exception as e:
            print(f"[{source.name} - Lỗi bóc tách link] {e}")

        return links

    def crawl_link_detail(self, url: str, source: Source) -> Optional[Article]:
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Tiêu đề
            title = ""
            if source.title_selector:
                title_el = soup.select_one(source.title_selector)
                if title_el:
                    title = title_el.get_text(strip=True)
            if not title:
                h1_el = soup.find("h1")
                if h1_el:
                    title = h1_el.get_text(strip=True)

            if not title:
                return None

            # 2. Tóm tắt (Sapo)
            summary = ""
            if source.description_selector:
                desc_el = soup.select_one(source.description_selector)
                if desc_el:
                    summary = desc_el.get_text(strip=True)
            if not summary:
                meta_desc = soup.select_one('meta[name="description"]') or soup.select_one('meta[property="og:description"]')
                if meta_desc:
                    summary = meta_desc.get("content", "").strip()

            # 3. Nội dung chi tiết
            content = ""
            if source.content_selector:
                content_el = soup.select_one(source.content_selector)
                if content_el:
                    paras = [p.get_text(strip=True) for p in content_el.find_all("p") if p.get_text(strip=True)]
                    content = "\n\n".join(paras) if paras else content_el.get_text(strip=True)

            if not content:
                # Fallback: lấy từ article tag hoặc body paragraphs
                art_tag = soup.find("article")
                if art_tag:
                    paras = [p.get_text(strip=True) for p in art_tag.find_all("p") if p.get_text(strip=True)]
                    content = "\n\n".join(paras)

            # 4. Ngày đăng
            published_date = ""
            if source.published_date_selector:
                date_el = soup.select_one(source.published_date_selector)
                if date_el:
                    published_date = date_el.get_text(strip=True)
            if not published_date:
                time_el = soup.find("time")
                if time_el:
                    published_date = time_el.get_text(strip=True)

            # 5. Tác giả
            author = ""
            if source.author_selector:
                author_el = soup.select_one(source.author_selector)
                if author_el:
                    author = author_el.get_text(strip=True)

            # 6. Thumbnail
            thumb_el = soup.select_one('meta[property="og:image"]')
            thumbnail_url = thumb_el.get("content", "") if thumb_el else ""

            return Article(
                source_id=source.id or 0,
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
            print(f"[{source.name} - Lỗi tải bài] {url}: {e}")
            return None
        except Exception as e:
            print(f"[{source.name} - Lỗi phân tích bài] {url}: {e}")
            return None

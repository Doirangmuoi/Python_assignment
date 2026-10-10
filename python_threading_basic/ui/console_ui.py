"""
Giao diện Console 2 tầng cho Hệ thống News Crawler
Xử lý hiển thị bảng biểu, phân trang bài viết, menu điều hướng và kiểm tra hợp lệ dữ liệu.
"""
import sys
import os
import textwrap
from datetime import datetime
from typing import List, Optional

from models.source import Source
from models.article import Article
from repositories.source_repository import SourceRepository
from repositories.article_repository import ArticleRepository
from services.crawler_factory import CrawlerFactory
from services.export_service import ExportService
from services.scheduler_service import SchedulerService
import config

# Cấu hình UTF-8 cho Terminal Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

class ConsoleUI:
    def __init__(self):
        self.source_repo = SourceRepository()
        self.article_repo = ArticleRepository()
        self.scheduler_service = SchedulerService(crawl_callback=self._scheduler_crawl_all)

    def _scheduler_crawl_all(self):
        """Hàm callback cho Scheduler chạy ngầm cào tất cả nguồn Active"""
        active_sources = self.source_repo.get_all(active_only=True)
        for src in active_sources:
            crawler = CrawlerFactory.get_crawler(src)
            crawler.crawl_source(src, self.article_repo, max_articles=15)

    def clear_screen(self):
        """Xóa màn hình console tùy theo hệ điều hành"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self):
        """Dừng màn hình chờ người dùng nhấn Enter"""
        print("\n" + "-" * 70)
        input("Nhấn [Enter] để tiếp tục...")

    # ==============================================================
    # 1. MENU CHÍNH (TẦNG 1)
    # ==============================================================
    def start(self):
        """Vòng lặp chính điều khiển chương trình (Main Loop)"""
        while True:
            self.clear_screen()
            sched_status = "ĐANG BẬT" if self.scheduler_service.is_running else "TẮT"
            print("=" * 70)
            print("        HỆ THỐNG TỔNG HỢP & QUẢN LÝ TIN TỨC ĐA NGUỒN (NEWS CRAWLER)")
            print(f"        [Database: MySQL | Auto Scheduler: {sched_status}]")
            print("=" * 70)
            print("1. Quản lý nguồn tin (Source Management)")
            print("2. Quản lý tin tức (News Article Management)")
            print("3. Chạy Crawler (Crawl Data)")
            print("4. Tự động hóa Crawler định kỳ (Scheduler)")
            print("5. Xuất báo cáo dữ liệu (CSV / Excel / JSON)")
            print("0. Thoát chương trình")
            print("-" * 70)
            
            choice = input("Nhập lựa chọn của bạn (0-5): ").strip()
            if choice == "1":
                self.menu_sources()
            elif choice == "2":
                self.menu_articles()
            elif choice == "3":
                self.menu_run_crawler()
            elif choice == "4":
                self.menu_scheduler()
            elif choice == "5":
                self.menu_export()
            elif choice == "0":
                print("\n[!] Đang đóng hệ thống và giải phóng tài nguyên...")
                if self.scheduler_service.is_running:
                    self.scheduler_service.stop()
                print("[+] Tạm biệt và hẹn gặp lại!")
                break
            else:
                print("\n[!] Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 5.")
                self.pause()

    # ==============================================================
    # 2. TẦNG 2A: MENU QUẢN LÝ NGUỒN TIN (SOURCE MANAGEMENT)
    # ==============================================================
    def menu_sources(self):
        while True:
            self.clear_screen()
            print("=" * 70)
            print("                   --- QUẢN LÝ NGUỒN TIN ---")
            print("=" * 70)
            print("1.1. Xem danh sách các nguồn tin")
            print("1.2. Thêm nguồn tin mới")
            print("1.3. Cập nhật thông tin nguồn tin")
            print("1.4. Xóa nguồn tin (hoặc đổi trạng thái Kích hoạt/Bỏ kích hoạt)")
            print("0.   Quay lại Menu chính")
            print("-" * 70)

            choice = input("Chọn chức năng (1.1 - 1.4 hoặc 0): ").strip()
            if choice in ["1.1", "1"]:
                self.view_source_list()
            elif choice in ["1.2", "2"]:
                self.add_source()
            elif choice in ["1.3", "3"]:
                self.update_source()
            elif choice in ["1.4", "4"]:
                self.delete_or_toggle_source()
            elif choice == "0":
                break
            else:
                print("\n[!] Lựa chọn không hợp lệ!")
                self.pause()

    def view_source_list(self):
        """1.1 Xem danh sách nguồn tin dạng bảng"""
        self.clear_screen()
        sources = self.source_repo.get_all()
        print("=" * 90)
        print(f"{'ID':<4} | {'Tên Nguồn':<16} | {'Trạng thái':<14} | {'Đường dẫn (URL)':<48}")
        print("=" * 90)
        if not sources:
            print("  Chưa có nguồn tin nào trong cơ sở dữ liệu.")
        else:
            for s in sources:
                st = "Đang Active" if s.is_active else "Tắt (Inactive)"
                print(f"{s.id:<4} | {s.name:<16} | {st:<14} | {s.url:<48}")
        print("=" * 90)
        self.pause()

    def add_source(self):
        """1.2 Thêm nguồn tin mới kèm CSS selectors"""
        self.clear_screen()
        print("=" * 70)
        print("                   THÊM NGUỒN TIN MỚI")
        print("=" * 70)
        name = input("Nhập tên nguồn tin (vd: Báo Lao Động): ").strip()
        if not name:
            print("[!] Tên nguồn không được để trống!")
            self.pause()
            return

        url = input("Nhập URL trang chủ/chuyên mục: ").strip()
        if not url or not url.startswith("http"):
            print("[!] URL phải bắt đầu bằng http:// hoặc https://!")
            self.pause()
            return

        print("\n--- Cấu hình CSS Selectors (Nhấn Enter để dùng mặc định) ---")
        list_sel = input("1. Selector lấy link bài viết [mặc định: a]: ").strip() or "a"
        title_sel = input("2. Selector lấy tiêu đề [mặc định: h1]: ").strip() or "h1"
        desc_sel = input("3. Selector lấy tóm tắt/sapo: ").strip()
        content_sel = input("4. Selector lấy nội dung [mặc định: article]: ").strip() or "article"
        author_sel = input("5. Selector lấy tác giả: ").strip()
        date_sel = input("6. Selector lấy ngày đăng: ").strip()

        src = Source(
            name=name,
            url=url,
            is_active=True,
            article_list_selector=list_sel,
            title_selector=title_sel,
            description_selector=desc_sel,
            content_selector=content_sel,
            author_selector=author_sel,
            published_date_selector=date_sel
        )

        try:
            new_id = self.source_repo.add(src)
            print(f"\n[+] Thêm nguồn tin thành công! ID mới: #{new_id}")
        except Exception as e:
            print(f"\n[!] Thất bại khi thêm nguồn tin: {e}")

        self.pause()

    def update_source(self):
        """1.3 Cập nhật nguồn tin"""
        self.clear_screen()
        sources = self.source_repo.get_all()
        print("Danh sách nguồn hiện tại:")
        for s in sources:
            print(f"  [#{s.id}] {s.name} - {s.url}")

        raw_id = input("\nNhập ID nguồn cần sửa (hoặc 0 để hủy): ").strip()
        if raw_id == "0" or not raw_id.isdigit():
            return

        source = self.source_repo.get_by_id(int(raw_id))
        if not source:
            print("[!] Không tìm thấy nguồn có ID này.")
            self.pause()
            return

        print(f"\nĐang sửa nguồn: #{source.id} - {source.name}")
        print("(Để trống và nhấn Enter nếu muốn giữ nguyên giá trị cũ)")

        new_name = input(f"Tên mới [{source.name}]: ").strip()
        new_url = input(f"URL mới [{source.url}]: ").strip()
        new_list_sel = input(f"Selector link bài [{source.article_list_selector}]: ").strip()
        new_title_sel = input(f"Selector tiêu đề [{source.title_selector}]: ").strip()
        new_desc_sel = input(f"Selector tóm tắt [{source.description_selector}]: ").strip()
        new_content_sel = input(f"Selector nội dung [{source.content_selector}]: ").strip()

        if new_name: source.name = new_name
        if new_url: source.url = new_url
        if new_list_sel: source.article_list_selector = new_list_sel
        if new_title_sel: source.title_selector = new_title_sel
        if new_desc_sel: source.description_selector = new_desc_sel
        if new_content_sel: source.content_selector = new_content_sel

        if self.source_repo.update(source):
            print("\n[+] Cập nhật thông tin nguồn thành công!")
        else:
            print("\n[!] Cập nhật thất bại hoặc dữ liệu không đổi.")
        self.pause()

    def delete_or_toggle_source(self):
        """1.4 Xóa hoặc Đổi trạng thái Kích hoạt/Bỏ kích hoạt"""
        self.clear_screen()
        sources = self.source_repo.get_all()
        print("Danh sách nguồn hiện tại:")
        for s in sources:
            st = "Active" if s.is_active else "Inactive"
            print(f"  [#{s.id}] {s.name} ({st}) - {s.url}")

        raw_id = input("\nNhập ID nguồn cần thao tác (hoặc 0 để hủy): ").strip()
        if raw_id == "0" or not raw_id.isdigit():
            return

        src_id = int(raw_id)
        source = self.source_repo.get_by_id(src_id)
        if not source:
            print("[!] Không tìm thấy nguồn.")
            self.pause()
            return

        print(f"\nBạn muốn làm gì với nguồn [#{source.id}] {source.name}?")
        print("1. Đổi trạng thái (Bật/Tắt Kích hoạt)")
        print("2. Xóa vĩnh viễn nguồn khỏi Database (Xóa toàn bộ bài viết liên quan)")
        print("0. Hủy bỏ")
        act = input("Chọn (1/2/0): ").strip()

        if act == "1":
            new_state = self.source_repo.toggle_active(src_id)
            status_str = "KÍCH HOẠT (Active)" if new_state else "BỎ KÍCH HOẠT (Inactive)"
            print(f"\n[+] Đã chuyển nguồn sang trạng thái: {status_str}")
        elif act == "2":
            confirm = input(f"Bạn có chắc muốn XÓA VĨNH VIỄN '{source.name}'? (y/N): ").strip().lower()
            if confirm == 'y':
                if self.source_repo.delete(src_id):
                    print("\n[+] Đã xóa nguồn thành công!")
                else:
                    print("\n[!] Lỗi khi xóa nguồn.")
            else:
                print("Đã hủy thao tác xóa.")
        self.pause()

    # ==============================================================
    # 3. TẦNG 2B: MENU QUẢN LÝ TIN TỨC (NEWS ARTICLE MANAGEMENT)
    # ==============================================================
    def menu_articles(self):
        while True:
            self.clear_screen()
            print("=" * 70)
            print("                   --- QUẢN LÝ TIN TỨC ---")
            print("=" * 70)
            print("2.1. Xem danh sách tin tức (Có phân trang bằng phím < và >)")
            print("2.2. Tìm kiếm tin tức (Theo tiêu đề hoặc từ khóa trong nội dung)")
            print("2.3. Lọc tin tức theo Nguồn (Source) hoặc Ngày cào")
            print("2.4. Xem chi tiết một bài viết")
            print("2.5. Xóa tin tức (Xóa bài trùng lặp hoặc bài quá cũ)")
            print("0.   Quay lại Menu chính")
            print("-" * 70)

            choice = input("Chọn chức năng (2.1 - 2.5 hoặc 0): ").strip()
            if choice in ["2.1", "1"]:
                self.view_articles_paginated()
            elif choice in ["2.2", "2"]:
                self.search_articles()
            elif choice in ["2.3", "3"]:
                self.filter_articles()
            elif choice in ["2.4", "4"]:
                self.view_article_detail_prompt()
            elif choice in ["2.5", "5"]:
                self.delete_articles_menu()
            elif choice == "0":
                break
            else:
                print("\n[!] Lựa chọn không hợp lệ!")
                self.pause()

    def view_articles_paginated(
        self,
        search_keyword: Optional[str] = None,
        source_id: Optional[int] = None,
        crawl_date: Optional[str] = None
    ):
        """2.1 Xem danh sách tin tức với phân trang bằng phím < và >"""
        page = 1
        page_size = config.DEFAULT_PAGE_SIZE

        while True:
            self.clear_screen()
            total_items = self.article_repo.count_articles(search_keyword, source_id, crawl_date)
            total_pages = max(1, (total_items + page_size - 1) // page_size)

            if page > total_pages:
                page = total_pages

            articles = self.article_repo.get_paginated(
                page=page,
                page_size=page_size,
                search_keyword=search_keyword,
                source_id=source_id,
                crawl_date=crawl_date
            )

            # Tiêu đề bảng
            filter_info = []
            if search_keyword: filter_info.append(f"Từ khóa: '{search_keyword}'")
            if source_id: filter_info.append(f"Source ID: {source_id}")
            if crawl_date: filter_info.append(f"Ngày cào: {crawl_date}")
            filter_str = f" [{', '.join(filter_info)}]" if filter_info else ""

            print("=" * 95)
            print(f" DANH SÁCH BÀI VIẾT TIN TỨC{filter_str}")
            print(f" Trang {page}/{total_pages} | Tổng số bài: {total_items}")
            print("=" * 95)
            print(f"{'ID':<6} | {'Nguồn':<12} | {'Ngày xuất bản':<18} | {'Tiêu đề bài viết':<52}")
            print("-" * 95)

            if not articles:
                print("  (Không có bài viết nào phù hợp)")
            else:
                for art in articles:
                    title_preview = art.title if len(art.title) <= 50 else art.title[:47] + "..."
                    src_name = art.source_name if len(art.source_name) <= 12 else art.source_name[:12]
                    pub_date = (art.published_date or "")[:18]
                    print(f"{art.id:<6} | {src_name:<12} | {pub_date:<18} | {title_preview:<52}")

            print("=" * 95)
            print("Điều hướng: [<] Trang trước | [>] Trang sau | [v <ID>] Xem chi tiết | [q] Thoát")
            cmd = input("Lệnh: ").strip().lower()

            if cmd in ["<", "p", "prev"]:
                if page > 1:
                    page -= 1
                else:
                    print("Đã ở trang đầu tiên!")
            elif cmd in [">", "n", "next"]:
                if page < total_pages:
                    page += 1
                else:
                    print("Đã ở trang cuối cùng!")
            elif cmd in ["q", "0", "exit", "back"]:
                break
            elif cmd.startswith("v "):
                parts = cmd.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    self.show_article_detail(int(parts[1]))
            elif cmd.isdigit():
                # Người dùng gõ trực tiếp ID bài viết
                self.show_article_detail(int(cmd))
            else:
                print("[!] Lệnh không hợp lệ.")

    def search_articles(self):
        """2.2 Tìm kiếm tin tức theo từ khóa"""
        self.clear_screen()
        print("=" * 70)
        print("                   TÌM KIẾM TIN TỨC")
        print("=" * 70)
        kw = input("Nhập từ khóa tìm kiếm (trong tiêu đề / tóm tắt / nội dung): ").strip()
        if not kw:
            print("[!] Từ khóa không được để trống!")
            self.pause()
            return
        self.view_articles_paginated(search_keyword=kw)

    def filter_articles(self):
        """2.3 Lọc tin tức theo Nguồn hoặc Ngày cào"""
        self.clear_screen()
        print("=" * 70)
        print("                   LỌC TIN TỨC")
        print("=" * 70)
        print("1. Lọc theo Nguồn tin (Source)")
        print("2. Lọc theo Ngày cào (Crawl Date)")
        print("3. Kết hợp lọc theo Nguồn VÀ Ngày cào")
        print("0. Hủy bỏ")
        opt = input("Chọn tùy chọn lọc (1-3): ").strip()

        source_id = None
        crawl_date = None

        if opt in ["1", "3"]:
            sources = self.source_repo.get_all()
            print("\nDanh sách nguồn tin:")
            for s in sources:
                print(f"  [#{s.id}] {s.name}")
            sid_input = input("Nhập ID nguồn cần lọc: ").strip()
            if sid_input.isdigit():
                source_id = int(sid_input)

        if opt in ["2", "3"]:
            cdate_input = input("\nNhập ngày cào (định dạng YYYY-MM-DD, vd 2026-10-06): ").strip()
            if cdate_input:
                crawl_date = cdate_input

        if opt in ["1", "2", "3"]:
            self.view_articles_paginated(source_id=source_id, crawl_date=crawl_date)

    def view_article_detail_prompt(self):
        """2.4 Nhập ID để xem chi tiết bài viết"""
        raw_id = input("\nNhập ID bài viết cần xem chi tiết: ").strip()
        if raw_id.isdigit():
            self.show_article_detail(int(raw_id))
        else:
            print("[!] ID phải là số nguyên.")
            self.pause()

    def show_article_detail(self, article_id: int):
        """Hiển thị chi tiết một bài viết với định dạng rõ ràng"""
        self.clear_screen()
        article = self.article_repo.get_by_id(article_id)
        if not article:
            print(f"[!] Không tìm thấy bài viết mang ID #{article_id} trong hệ thống.")
            self.pause()
            return

        print("=" * 80)
        print(f" BÀI VIẾT #{article.id} | Nguồn: {article.source_name}")
        print("=" * 80)
        print(f"Tiêu đề       : {article.title}")
        print(f"Tác giả       : {article.author or 'Không rõ'}")
        print(f"Ngày đăng     : {article.published_date or 'N/A'}")
        print(f"Thời gian cào : {article.crawled_at}")
        print(f"Đường dẫn gốc : {article.url}")
        print("-" * 80)
        print("TÓM TẮT (SAPO):")
        wrapped_summary = textwrap.fill(article.summary or "(Không có tóm tắt)", width=78)
        print(wrapped_summary)
        print("-" * 80)
        print("NỘI DUNG CHI TIẾT:")
        if article.content:
            for p in article.content.split("\n\n"):
                if p.strip():
                    print(textwrap.fill(p.strip(), width=78))
                    print()
        else:
            print("(Nội dung bài viết rỗng)")
        print("=" * 80)
        self.pause()

    def delete_articles_menu(self):
        """2.5 Xóa tin tức (Xóa theo ID, Xóa bài quá cũ, Xóa bài trùng lặp)"""
        self.clear_screen()
        print("=" * 70)
        print("                   XÓA BÀI VIẾT TIN TỨC")
        print("=" * 70)
        print("1. Xóa một bài viết theo ID")
        print("2. Xóa các bài viết quá cũ (cũ hơn N ngày)")
        print("3. Quét & Xóa các bài viết trùng lặp URL")
        print("0. Quay lại")
        print("-" * 70)

        opt = input("Chọn thao tác (1-3 hoặc 0): ").strip()
        if opt == "1":
            raw_id = input("Nhập ID bài viết cần xóa: ").strip()
            if raw_id.isdigit():
                art_id = int(raw_id)
                if self.article_repo.delete_by_id(art_id):
                    print(f"[+] Đã xóa thành công bài viết #{art_id}!")
                else:
                    print(f"[!] Không tìm thấy bài viết #{art_id} để xóa.")
            self.pause()
        elif opt == "2":
            days_input = input("Nhập số ngày (vd: 30 ngày để xóa bài cào cách đây hơn 30 ngày): ").strip()
            if days_input.isdigit():
                days = int(days_input)
                deleted = self.article_repo.delete_older_than(days)
                print(f"[+] Đã xóa {deleted} bài viết cũ hơn {days} ngày!")
            self.pause()
        elif opt == "3":
            deleted = self.article_repo.delete_duplicates()
            print(f"[+] Đã dọn dẹp {deleted} bài viết trùng lặp URL trong cơ sở dữ liệu!")
            self.pause()

    # ==============================================================
    # 4. CHỨC NĂNG CHẠY CRAWLER (OPTION 3)
    # ==============================================================
    def menu_run_crawler(self):
        self.clear_screen()
        print("=" * 70)
        print("                   CHẠY BỘ THU THẬP DỮ LIỆU (CRAWLER)")
        print("=" * 70)
        print("1. Cào từ TẤT CẢ các nguồn đang kích hoạt (Active)")
        print("2. Chọn MỘT nguồn tin cụ thể để cào")
        print("0. Quay lại Menu chính")
        print("-" * 70)

        opt = input("Chọn hình thức cào (1/2/0): ").strip()
        if opt == "0":
            return

        target_sources = []
        if opt == "1":
            target_sources = self.source_repo.get_all(active_only=True)
            if not target_sources:
                print("[!] Không có nguồn tin nào đang ở trạng thái Active!")
                self.pause()
                return
        elif opt == "2":
            sources = self.source_repo.get_all()
            print("\nDanh sách các nguồn tin:")
            for s in sources:
                st = "Active" if s.is_active else "Inactive"
                print(f"  [#{s.id}] {s.name} ({st}) - {s.url}")
            sid_input = input("\nNhập ID nguồn cần cào: ").strip()
            if not sid_input.isdigit():
                return
            src = self.source_repo.get_by_id(int(sid_input))
            if not src:
                print("[!] Không tìm thấy nguồn.")
                self.pause()
                return
            target_sources = [src]
        else:
            print("[!] Lựa chọn không hợp lệ.")
            self.pause()
            return

        limit_input = input("Số lượng bài tối đa cần cào mỗi nguồn [mặc định 15]: ").strip()
        max_articles = int(limit_input) if limit_input.isdigit() else 15

        print(f"\n[*] Bắt đầu cào {len(target_sources)} nguồn tin với giới hạn {max_articles} bài/nguồn...")
        
        grand_total_new = 0
        grand_total_updated = 0

        for src in target_sources:
            crawler = CrawlerFactory.get_crawler(src)
            result = crawler.crawl_source(src, self.article_repo, max_articles=max_articles)
            grand_total_new += result.get("new", 0)
            grand_total_updated += result.get("updated", 0)

        print("=" * 70)
        print(f"[+] TỔNG KẾT: Thêm mới {grand_total_new} bài | Cập nhật {grand_total_updated} bài!")
        print("=" * 70)
        self.pause()

    # ==============================================================
    # 5. TỰ ĐỘNG HÓA SCHEDULER (ĐIỂM CỘNG +0.5đ)
    # ==============================================================
    def menu_scheduler(self):
        while True:
            self.clear_screen()
            status = self.scheduler_service.get_status()
            st_text = "ĐANG CHẠY" if status["is_running"] else "ĐÃ DỪNG"

            print("=" * 70)
            print("         TỰ ĐỘNG HÓA CRAWLER ĐỊNH KỲ (SCHEDULER SERVICE)")
            print("=" * 70)
            print(f"Trạng thái      : {st_text}")
            print(f"Chu kỳ chạy     : Mỗi {status['interval_minutes']} phút")
            print(f"Lần chạy trước  : {status['last_run']}")
            print(f"Lần chạy tiếp   : {status['next_run']}")
            print(f"Tổng số lần chạy: {status['run_count']}")
            print("-" * 70)
            print("1. Khởi động chạy tự động (Đặt lịch chu kỳ mới)")
            print("2. Dừng chạy tự động")
            print("3. Kích hoạt cào ngay lập tức")
            print("0. Quay lại Menu chính")
            print("-" * 70)

            ch = input("Chọn chức năng (1-3 hoặc 0): ").strip()
            if ch == "1":
                mins = input("Nhập số phút giữa các lần cào [mặc định 30]: ").strip()
                interval = int(mins) if mins.isdigit() and int(mins) > 0 else 30
                self.scheduler_service.start(interval_minutes=interval)
                print(f"[+] Đã khởi động Scheduler cào tự động mỗi {interval} phút!")
                self.pause()
            elif ch == "2":
                if self.scheduler_service.stop():
                    print("[+] Đã dừng Scheduler thành công.")
                else:
                    print("[!] Scheduler hiện không chạy.")
                self.pause()
            elif ch == "3":
                print("[*] Đang kích hoạt cào tin tức toàn bộ nguồn...")
                self._scheduler_crawl_all()
                self.pause()
            elif ch == "0":
                break

    # ==============================================================
    # 6. XUẤT BÁO CÁO DỮ LIỆU (ĐIỂM CỘNG +0.5đ)
    # ==============================================================
    def menu_export(self):
        self.clear_screen()
        print("=" * 70)
        print("          XUẤT BÁO CÁO DANH SÁCH TIN TỨC (EXPORT DATA)")
        print("=" * 70)
        print("1. Xuất file Excel (.xlsx) [Đẹp mắt, có định dạng ô]")
        print("2. Xuất file CSV (Chuẩn bảng mã UTF-8-SIG cho tiếng Việt)")
        print("3. Xuất file JSON (Dữ liệu có cấu trúc)")
        print("4. Xuất TẤT CẢ 3 định dạng trên")
        print("0. Quay lại Menu chính")
        print("-" * 70)

        opt = input("Chọn định dạng xuất (1-4 hoặc 0): ").strip()
        if opt == "0":
            return

        articles = self.article_repo.get_all_for_export()
        if not articles:
            print("[!] Không có bài viết nào trong CSDL để xuất báo cáo.")
            self.pause()
            return

        print(f"\n[*] Đang xuất báo cáo cho {len(articles)} bài viết...")
        exported_files = []

        if opt in ["1", "4"]:
            f_excel = ExportService.export_to_excel(articles)
            exported_files.append(("Excel (.xlsx)", f_excel))

        if opt in ["2", "4"]:
            f_csv = ExportService.export_to_csv(articles)
            exported_files.append(("CSV (.csv)", f_csv))

        if opt in ["3", "4"]:
            f_json = ExportService.export_to_json(articles)
            exported_files.append(("JSON (.json)", f_json))

        print("\n" + "=" * 70)
        print("[+] XUẤT BÁO CÁO THÀNH CÔNG:")
        for fmt, path in exported_files:
            print(f" - {fmt:<14}: {path}")
        print("=" * 70)
        self.pause()

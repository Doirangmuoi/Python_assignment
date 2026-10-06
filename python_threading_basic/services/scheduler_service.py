"""
Dịch vụ tự động hóa lịch cào tin tức định kỳ bằng thư viện schedule (Điểm cộng +0.5đ)
"""
import time
import threading
from datetime import datetime
from typing import Optional, Callable
import schedule

class SchedulerService:
    def __init__(self, crawl_callback: Optional[Callable] = None):
        """
        :param crawl_callback: Hàm thực thi cào tin (thường là cào tất cả nguồn Active)
        """
        self.crawl_callback = crawl_callback
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.interval_minutes = 30
        self.last_run: Optional[datetime] = None
        self.run_count = 0

    def _job_wrapper(self):
        print(f"\n[Scheduler] Đang tự động kích hoạt cào tin theo lịch ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})...")
        self.last_run = datetime.now()
        self.run_count += 1
        if self.crawl_callback:
            try:
                self.crawl_callback()
            except Exception as e:
                print(f"[Scheduler - Lỗi thực thi Job] {e}")
        print("[Scheduler] Hoàn tất phiên cào tin tự động. Đang đợi lượt tiếp theo...")

    def _loop(self):
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def start(self, interval_minutes: int = 30) -> bool:
        """Khởi động bộ lập lịch trong luồng ngầm (Background Thread)"""
        if self.is_running:
            return False

        self.interval_minutes = interval_minutes
        self._stop_event.clear()
        schedule.clear()

        # Đặt lịch định kỳ theo số phút
        schedule.every(interval_minutes).minutes.do(self._job_wrapper)

        self._thread = threading.Thread(target=self._loop, daemon=True, name="NewsCrawlerScheduler")
        self._thread.start()
        self.is_running = True
        return True

    def stop(self) -> bool:
        """Dừng bộ lập lịch định kỳ"""
        if not self.is_running:
            return False

        self._stop_event.set()
        schedule.clear()
        self.is_running = False
        return True

    def get_status(self) -> dict:
        """Lấy thông tin trạng thái của Scheduler"""
        next_run_str = "Chưa có"
        jobs = schedule.get_jobs()
        if jobs and jobs[0].next_run:
            next_run_str = jobs[0].next_run.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "is_running": self.is_running,
            "interval_minutes": self.interval_minutes,
            "last_run": self.last_run.strftime("%Y-%m-%d %H:%M:%S") if self.last_run else "Chưa chạy",
            "next_run": next_run_str if self.is_running else "Đã dừng",
            "run_count": self.run_count
        }

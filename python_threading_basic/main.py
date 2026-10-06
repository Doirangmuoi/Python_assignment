"""
BÀI TẬP LỚN PYTHON: ỨNG DỤNG THU THẬP VÀ QUẢN LÝ TIN TỨC ĐA NGUỒN (NEWS CRAWLER)
Điểm khởi đầu chính của chương trình (Entry Point).
"""
import sys
from database.db_connection import DatabaseConnection
from ui.console_ui import ConsoleUI

def main():
    # Cấu hình UTF-8 cho Terminal Windows
    if sys.platform.startswith('win'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stdin.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("[*] Đang khởi động hệ thống News Crawler...")
    print("[*] Kiểm tra và khởi tạo Cơ sở dữ liệu MySQL...")

    # Khởi tạo CSDL MySQL (tạo database, tạo bảng và nạp seed data nếu chưa có)
    if not DatabaseConnection.init_database():
        print("\n" + "!" * 70)
        print("[LỖI NGHIÊM TRỌNG] Không thể kết nối hoặc khởi tạo CSDL MySQL!")
        print("Vui lòng kiểm tra lại:")
        print("  1. Dịch vụ MySQL Server (XAMPP / WampServer / MySQL Service) đã bật chưa?")
        print("  2. Cấu hình DB_HOST, DB_PORT, DB_USER, DB_PASSWORD trong config.py.")
        print("!" * 70)
        input("\nNhấn [Enter] để thoát...")
        sys.exit(1)

    print("[+] Kết nối MySQL thành công! Đang tải giao diện Menu...")

    try:
        app = ConsoleUI()
        app.start()
    except KeyboardInterrupt:
        print("\n\n[!] Đã nhận tín hiệu dừng (Ctrl+C). Đang thoát chương trình...")
    except Exception as e:
        print(f"\n[!] Lỗi không xác định: {e}")
        input("Nhấn [Enter] để thoát...")

if __name__ == "__main__":
    main()
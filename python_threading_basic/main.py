"""
BÀI TẬP LỚN PYTHON: ỨNG DỤNG THU THẬP VÀ QUẢN LÝ TIN TỨC ĐA NGUỒN (NEWS CRAWLER)
Điểm khởi đầu chính của chương trình (Entry Point).
"""
import sys
import os

# Tự động phát hiện và chuyển sang môi trường ảo .venv nếu đang dùng Python toàn cục
venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and os.path.normcase(os.path.abspath(sys.executable)) != os.path.normcase(os.path.abspath(venv_python)):
    import subprocess
    try:
        proc = subprocess.run([venv_python, os.path.abspath(__file__)] + sys.argv[1:])
        sys.exit(proc.returncode)
    except Exception:
        pass

try:
    from database.db_connection import DatabaseConnection
    from ui.console_ui import ConsoleUI
except ModuleNotFoundError as err:
    print(f"\n[!] Lỗi thiếu thư viện: {err}")
    print("Vui lòng kích hoạt virtual environment trước khi chạy:")
    print(r"    .\.venv\Scripts\activate")
    print("    python main.py")
    print("Hoặc cài đặt thư viện vào Python hiện tại:")
    print(r"    pip install -r requirements.txt")
    sys.exit(1)

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
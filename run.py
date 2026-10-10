"""
Script chạy ứng dụng từ thư mục gốc
"""
import sys
import os

# Tự động phát hiện và chuyển sang môi trường ảo .venv nếu đang dùng Python toàn cục
venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python_threading_basic", ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and os.path.normcase(os.path.abspath(sys.executable)) != os.path.normcase(os.path.abspath(venv_python)):
    import subprocess
    try:
        proc = subprocess.run([venv_python, os.path.abspath(__file__)] + sys.argv[1:])
        sys.exit(proc.returncode)
    except Exception:
        pass

# Thêm thư mục mã nguồn con vào sys.path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python_threading_basic")
sys.path.insert(0, app_dir)

try:
    from main import main
except ModuleNotFoundError as err:
    print(f"\n[!] Lỗi thiếu thư viện: {err}")
    print("Vui lòng kích hoạt virtual environment trước khi chạy:")
    print(r"    .\python_threading_basic\.venv\Scripts\activate")
    print("    python run.py")
    print("Hoặc cài đặt thư viện vào Python hiện tại:")
    print(r"    pip install -r .\python_threading_basic\requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    main()


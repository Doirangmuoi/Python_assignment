"""
Script chạy ứng dụng từ thư mục gốc
"""
import sys
import os

# Thêm thư mục mã nguồn con vào sys.path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python_threading_basic")
sys.path.insert(0, app_dir)

from main import main

if __name__ == "__main__":
    main()

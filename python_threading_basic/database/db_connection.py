"""
Module quản lý kết nối CSDL MySQL và tự động khởi tạo bảng.
"""
import os
import mysql.connector
from mysql.connector import errorcode, Error
import config

class DatabaseConnection:
    @staticmethod
    def get_connection(use_database: bool = True):
        """
        Tạo kết nối tới MySQL.
        :param use_database: True nếu muốn kết nối trực tiếp vào DB config.DB_NAME,
                             False nếu kết nối root server để tạo database.
        """
        try:
            conn_params = {
                "host": config.DB_HOST,
                "port": config.DB_PORT,
                "user": config.DB_USER,
                "password": config.DB_PASSWORD,
                "charset": "utf8mb4",
                "use_unicode": True,
                "autocommit": True
            }
            if use_database:
                conn_params["database"] = config.DB_NAME

            return mysql.connector.connect(**conn_params)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(f"[LỖI MYSQL] Sai tài khoản hoặc mật khẩu kết nối MySQL (User: '{config.DB_USER}').")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"[LỖI MYSQL] Database '{config.DB_NAME}' chưa tồn tại. Sẽ tự động khởi tạo...")
            else:
                print(f"[LỖI MYSQL] Không thể kết nối tới MySQL ({config.DB_HOST}:{config.DB_PORT}): {err}")
            raise err

    @classmethod
    def init_database(cls) -> bool:
        """
        Khởi tạo Database, các Bảng và Dữ liệu mẫu từ file schema.sql.
        Trả về True nếu thành công, False nếu thất bại.
        """
        try:
            # 1. Kết nối không chọn DB để tạo DB nếu chưa có
            conn = cls.get_connection(use_database=False)
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.close()
            conn.close()

            # 2. Kết nối vào DB vừa tạo và chạy lệnh từ schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_content = f.read()

                # Tách từng câu lệnh SQL (loại bỏ comment và khoảng trắng thừa)
                conn = cls.get_connection(use_database=True)
                cursor = conn.cursor()
                
                # Chạy từng khối câu lệnh
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for statement in statements:
                    # Bỏ qua các lệnh USE vì đã chọn database
                    if statement.upper().startswith("USE "):
                        continue
                    try:
                        cursor.execute(statement)
                    except mysql.connector.Error as e:
                        # Bỏ qua nếu lỗi nhẹ hoặc bảng đã tồn tại
                        pass
                
                cursor.close()
                conn.close()
                return True
            else:
                print(f"[CẢNH BÁO] Không tìm thấy file {schema_path}")
                return False

        except Exception as e:
            print(f"[LỖI KHỞI TẠO CSDL] {e}")
            return False

    @classmethod
    def test_connection(cls) -> bool:
        """Kiểm tra trạng thái kết nối tới MySQL server"""
        try:
            conn = cls.get_connection(use_database=True)
            if conn.is_connected():
                conn.close()
                return True
            return False
        except Exception:
            return False

"""
Dịch vụ xuất dữ liệu báo cáo ra các định dạng: CSV, Excel (.xlsx), JSON (Điểm cộng +0.5đ)
"""
import os
import csv
import json
from datetime import datetime
from typing import List, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from models.article import Article
import config

class ExportService:
    @staticmethod
    def _generate_filename(prefix: str, extension: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(config.EXPORT_DIR, f"{prefix}_{timestamp}.{extension}")

    @classmethod
    def export_to_csv(cls, articles: List[Article], filename: Optional[str] = None) -> str:
        """
        Xuất danh sách bài viết ra file CSV với bảng mã UTF-8-SIG (chuẩn tiếng Việt cho Excel)
        """
        if not filename:
            filename = cls._generate_filename("news_report", "csv")

        fields = [
            "ID", "Nguồn", "Tiêu đề", "Tóm tắt", "Nội dung", 
            "Tác giả", "Ngày xuất bản", "Đường dẫn gốc", "Ngày cào", "Trạng thái"
        ]

        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for art in articles:
                writer.writerow([
                    art.id,
                    art.source_name,
                    art.title,
                    art.summary,
                    art.content[:2000] if art.content else "",  # Giới hạn tránh tràn ô CSV
                    art.author,
                    art.published_date,
                    art.url,
                    str(art.crawled_at),
                    art.status
                ])

        return filename

    @classmethod
    def export_to_json(cls, articles: List[Article], filename: Optional[str] = None) -> str:
        """
        Xuất danh sách bài viết ra file JSON có format đẹp
        """
        if not filename:
            filename = cls._generate_filename("news_report", "json")

        data = [art.to_dict() for art in articles]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filename

    @classmethod
    def export_to_excel(cls, articles: List[Article], filename: Optional[str] = None) -> str:
        """
        Xuất danh sách bài viết ra file Excel (.xlsx) với định dạng bảng chuyên nghiệp bằng openpyxl
        """
        if not filename:
            filename = cls._generate_filename("news_report", "xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Danh sách Tin tức"

        # Định nghĩa tiêu đề cột
        headers = [
            "ID", "Nguồn tin", "Tiêu đề bài viết", "Tóm tắt (Sapo)", 
            "Tác giả", "Ngày xuất bản", "Đường dẫn gốc", "Thời gian cào", "Trạng thái"
        ]

        # Định dạng Header
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        alignment_center = Alignment(horizontal="center", vertical="center")
        border_thin = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        ws.append(headers)

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = alignment_center
            cell.border = border_thin
        ws.row_dimensions[1].height = 28

        # Điền dữ liệu các dòng
        for row_idx, art in enumerate(articles, start=2):
            row_data = [
                art.id,
                art.source_name,
                art.title,
                art.summary,
                art.author,
                art.published_date,
                art.url,
                str(art.crawled_at),
                art.status
            ]
            ws.append(row_data)

            # Style từng ô trong hàng
            for col_num in range(1, len(row_data) + 1):
                c = ws.cell(row=row_idx, column=col_num)
                c.border = border_thin
                c.alignment = Alignment(vertical="center", wrap_text=False)
            ws.row_dimensions[row_idx].height = 20

        # Tự động căn chỉnh độ rộng cột
        col_widths = {
            1: 8,   # ID
            2: 15,  # Nguồn
            3: 45,  # Tiêu đề
            4: 45,  # Tóm tắt
            5: 18,  # Tác giả
            6: 22,  # Ngày xuất bản
            7: 40,  # URL
            8: 20,  # Thời gian cào
            9: 14   # Trạng thái
        }
        for col_idx, width in col_widths.items():
            ws.column_dimensions[get_column_letter(col_idx)].width = width

        wb.save(filename)
        return filename

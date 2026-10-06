"""
Tương thích với tên file cũ news.repositories.py
Chuyển tiếp (forward) các thao tác sang ArticleRepository.
"""
from repositories.article_repository import ArticleRepository

# Alias cho NewsRepository
NewsRepository = ArticleRepository

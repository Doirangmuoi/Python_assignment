-- =======================================================
-- BÀI TẬP LỚN PYTHON: NEWS CRAWLER DATABASE SCHEMA
-- Hệ thống CSDL MySQL Quản lý & Thu thập Tin tức đa nguồn
-- =======================================================

CREATE DATABASE IF NOT EXISTS news_crawler_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE news_crawler_db;

-- 1. BẢNG NGUỒN TIN (sources)
CREATE TABLE IF NOT EXISTS sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT 'Tên nguồn tin tức (vd: VnExpress, Tuổi Trẻ, Dân Trí)',
    url VARCHAR(255) NOT NULL COMMENT 'Đường dẫn trang chủ hoặc chuyên mục',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Trạng thái hoạt động: 1 = Active, 0 = Inactive',
    article_list_selector VARCHAR(255) DEFAULT '' COMMENT 'CSS Selector để lấy link các bài viết trong danh sách',
    title_selector VARCHAR(255) DEFAULT '' COMMENT 'CSS Selector lấy tiêu đề bài viết',
    description_selector VARCHAR(255) DEFAULT '' COMMENT 'CSS Selector lấy tóm tắt/sapo',
    content_selector VARCHAR(255) DEFAULT '' COMMENT 'CSS Selector lấy nội dung chi tiết bài viết',
    author_selector VARCHAR(255) DEFAULT '' COMMENT 'CSS Selector lấy tác giả bài viết',
    published_date_selector VARCHAR(255) DEFAULT '' COMMENT 'CSS Selector lấy ngày đăng bài viết',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_source_status (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. BẢNG TIN TỨC (articles)
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_id INT NOT NULL COMMENT 'Khóa ngoại liên kết tới bảng sources',
    url VARCHAR(500) NOT NULL COMMENT 'Đường dẫn gốc bài viết (unique để chống trùng lặp)',
    title VARCHAR(500) NOT NULL COMMENT 'Tiêu đề bài viết',
    summary TEXT NULL COMMENT 'Tóm tắt / sapo bài viết',
    content LONGTEXT NULL COMMENT 'Nội dung chi tiết bài viết',
    author VARCHAR(150) NULL COMMENT 'Tác giả bài viết',
    published_date VARCHAR(100) NULL COMMENT 'Thời gian xuất bản bài viết',
    thumbnail_url VARCHAR(500) NULL COMMENT 'Đường dẫn ảnh đại diện bài viết',
    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm cào dữ liệu vào hệ thống',
    status ENUM('PENDING', 'COMPLETED', 'FAILED') DEFAULT 'COMPLETED' COMMENT 'Trạng thái cào chi tiết',
    
    -- Khóa ngoại liên kết bảng nguồn tin (kèm ON DELETE CASCADE khi xóa nguồn)
    CONSTRAINT fk_articles_source
        FOREIGN KEY (source_id) REFERENCES sources (id)
        ON DELETE CASCADE,
        
    -- Ràng buộc Unique & Index để chống trùng lặp link và tăng tốc tìm kiếm
    UNIQUE KEY uq_article_url (url(255)),
    INDEX idx_article_source (source_id),
    INDEX idx_article_crawled_at (crawled_at),
    INDEX idx_article_title (title(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. DỮ LIỆU KHỞI TẠO MẪU (SEED DATA - 3 NGUỒN BÁO UY TÍN)
INSERT INTO sources (id, name, url, is_active, article_list_selector, title_selector, description_selector, content_selector, author_selector, published_date_selector)
VALUES 
(
    1, 
    'VnExpress', 
    'https://vnexpress.net/thoi-su', 
    1, 
    'article.item-news h3.title-news a, h3.title-news a', 
    'h1.title-detail', 
    'p.description', 
    'article.fck_detail', 
    'p.author_mail, p.Normal strong', 
    'span.date'
),
(
    2, 
    'Dân Trí', 
    'https://dantri.com.vn/xa-hoi.htm', 
    1, 
    'article.article-item h3.article-title a, h3.article-title a', 
    'article h1, h1.title-page', 
    'article h2, h2.singular-sapo', 
    'article .singular-content, article', 
    'article .author-name, article p strong', 
    'time.author-time, .author-time'
),
(
    3, 
    'Tuổi Trẻ', 
    'https://tuoitre.vn/thoi-su.htm', 
    1, 
    'div.box-category-item a, h3.box-title-text a, a[href$=".htm"]', 
    'h1.detail-title, h1.article-title, h1', 
    'h2.detail-sapo, h2.article-sapo', 
    'div.detail-content, div.article-content', 
    'div.author-info, .detail-author', 
    'div.detail-time, div.article-date'
)
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    url = VALUES(url),
    is_active = VALUES(is_active),
    article_list_selector = VALUES(article_list_selector),
    title_selector = VALUES(title_selector),
    description_selector = VALUES(description_selector),
    content_selector = VALUES(content_selector);

create database agentSystemV2;

-- Включение необходимых расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 1. Таблица пользователей
-- ============================================
CREATE TABLE Users (
    Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Username VARCHAR(100) UNIQUE NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    FullName TEXT NOT NULL,
    IsActive BOOLEAN DEFAULT true,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
    -- CONSTRAINT chk_email_format CHECK (Email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    -- CONSTRAINT chk_username_length CHECK (LENGTH(Username) >= 3)
);

-- Индекс для быстрого поиска пользователей по email
CREATE INDEX idx_users_email ON Users(Email);
CREATE INDEX idx_users_username ON Users(Username);

-- ============================================
-- 2. Таблица категорий
-- ============================================
CREATE TABLE Categories (
    Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Name TEXT NOT NULL,
    ParentId UUID,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL,
    
    CONSTRAINT fk_parent_category 
        FOREIGN KEY (ParentId) 
        REFERENCES Categories(Id) 
        ON DELETE SET NULL,
    
    CONSTRAINT fk_category_createdby 
        FOREIGN KEY (CreatedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
        
    CONSTRAINT fk_category_modifiedby 
        FOREIGN KEY (ModifiedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
    
    -- Категория не может быть родителем самой себе
    CONSTRAINT chk_not_self_parent 
        CHECK (ParentId IS NULL OR ParentId != Id),
    
    -- Уникальность имени в рамках одного уровня иерархии
    CONSTRAINT uniq_category_name_per_parent 
        UNIQUE (Name, ParentId)
);

-- Индексы для категорий
CREATE INDEX idx_categories_parentid ON Categories(ParentId);
CREATE INDEX idx_categories_createdby ON Categories(CreatedBy);
CREATE INDEX idx_categories_modifiedby ON Categories(ModifiedBy);

-- ============================================
-- 3. Таблица документов
-- ============================================
CREATE TABLE Documents (
    Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Title TEXT NOT NULL,
    FileName TEXT NOT NULL,
    Extension VARCHAR(20) NOT NULL,
    SizeBytes BIGINT NOT NULL CHECK (SizeBytes >= 0),
    Status VARCHAR(50) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL,
    
    CONSTRAINT fk_document_createdby 
        FOREIGN KEY (CreatedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
        
    CONSTRAINT fk_document_modifiedby 
        FOREIGN KEY (ModifiedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
    
    CONSTRAINT chk_valid_status 
        CHECK (Status IN ('draft', 'processing', 'active', 'archived', 'deleted'))
);

-- Индексы для документов
CREATE INDEX idx_documents_status ON Documents(Status);
CREATE INDEX idx_documents_createdat ON Documents(CreatedAt);
CREATE INDEX idx_documents_modifiedat ON Documents(ModifiedAt);
CREATE INDEX idx_documents_createdby ON Documents(CreatedBy);
CREATE INDEX idx_documents_modifiedby ON Documents(ModifiedBy);
CREATE INDEX idx_documents_extension ON Documents(Extension);

-- ============================================
-- 4. Таблица связей документов и категорий
-- ============================================
CREATE TABLE DocumentCategories (
    DocumentId UUID NOT NULL,
    CategoryId UUID NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL,
    
    PRIMARY KEY (DocumentId, CategoryId),
    
    CONSTRAINT fk_documentcategories_document 
        FOREIGN KEY (DocumentId) 
        REFERENCES Documents(Id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_documentcategories_category 
        FOREIGN KEY (CategoryId) 
        REFERENCES Categories(Id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_documentcategories_createdby 
        FOREIGN KEY (CreatedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
        
    CONSTRAINT fk_documentcategories_modifiedby 
        FOREIGN KEY (ModifiedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT
);

-- Индексы для связей документ-категория
CREATE INDEX idx_documentcategories_documentid ON DocumentCategories(DocumentId);
CREATE INDEX idx_documentcategories_categoryid ON DocumentCategories(CategoryId);
CREATE INDEX idx_documentcategories_createdby ON DocumentCategories(CreatedBy);

-- ============================================
-- 5. Таблица чанков документов с векторами
-- ============================================
CREATE TABLE Chunks (
    Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    DocumentId UUID NOT NULL,
    ChunkIndex INTEGER NOT NULL CHECK (ChunkIndex >= 0),
    Text TEXT NOT NULL,
    Embedding vector(1536),
    Metadata JSONB DEFAULT '{}'::jsonb,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL,
    
    CONSTRAINT fk_chunks_document 
        FOREIGN KEY (DocumentId) 
        REFERENCES Documents(Id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_chunks_createdby 
        FOREIGN KEY (CreatedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
        
    CONSTRAINT fk_chunks_modifiedby 
        FOREIGN KEY (ModifiedBy)
        REFERENCES Users(Id)
        ON DELETE RESTRICT,
    
    CONSTRAINT unique_document_chunk_index 
        UNIQUE (DocumentId, ChunkIndex),
    
    -- Проверка, что текст не пустой
    CONSTRAINT chk_text_not_empty 
        CHECK (LENGTH(TRIM(Text)) > 0),
    
    -- Проверка на максимальную длину чанка (опционально)
    CONSTRAINT chk_max_chunk_size 
        CHECK (LENGTH(Text) <= 10000)
);

-- Индексы для чанков
CREATE INDEX idx_chunks_documentid ON Chunks(DocumentId);
CREATE INDEX idx_chunks_chunkindex ON Chunks(ChunkIndex);
CREATE INDEX idx_chunks_embedding ON Chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_metadata ON Chunks USING gin (Metadata);
CREATE INDEX idx_chunks_createdby ON Chunks(CreatedBy);
CREATE INDEX idx_chunks_createdat ON Chunks(CreatedAt);

-- ============================================
-- 6. Функция и триггеры для обновления ModifiedAt
-- ============================================
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ModifiedAt = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для автоматического обновления времени модификации
CREATE TRIGGER update_users_modified_at
    BEFORE UPDATE ON Users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

CREATE TRIGGER update_categories_modified_at
    BEFORE UPDATE ON Categories
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

CREATE TRIGGER update_documents_modified_at
    BEFORE UPDATE ON Documents
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

CREATE TRIGGER update_documentcategories_modified_at
    BEFORE UPDATE ON DocumentCategories
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

CREATE TRIGGER update_chunks_modified_at
    BEFORE UPDATE ON Chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- ============================================
-- 7. Дополнительные проверочные функции
-- ============================================

-- Функция для проверки циклических ссылок в категориях
CREATE OR REPLACE FUNCTION check_category_cycle()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ParentId IS NOT NULL THEN
        -- Проверяем, не создается ли циклическая ссылка
        WITH RECURSIVE CategoryPath AS (
            SELECT Id, ParentId
            FROM Categories
            WHERE Id = NEW.ParentId
            UNION ALL
            SELECT c.Id, c.ParentId
            FROM Categories c
            INNER JOIN CategoryPath cp ON c.Id = cp.ParentId
        )
        SELECT COUNT(*) INTO cycle_count
        FROM CategoryPath
        WHERE Id = NEW.Id;
        
        IF cycle_count > 0 THEN
            RAISE EXCEPTION 'Циклическая ссылка обнаружена в иерархии категорий';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_category_cycle
    BEFORE INSERT OR UPDATE ON Categories
    FOR EACH ROW
    EXECUTE FUNCTION check_category_cycle();

-- ============================================
-- 8. Представления для удобства работы
-- ============================================

-- Представление для получения документов с информацией о пользователях
CREATE VIEW DocumentsWithUsers AS
SELECT 
    d.*,
    uc.FullName as CreatedByFullName,
    uc.Email as CreatedByEmail,
    um.FullName as ModifiedByFullName,
    um.Email as ModifiedByEmail
FROM Documents d
LEFT JOIN Users uc ON d.CreatedBy = uc.Id
LEFT JOIN Users um ON d.ModifiedBy = um.Id;

-- Представление для иерархии категорий с путями
CREATE VIEW CategoryHierarchy AS
WITH RECURSIVE CategoryTree AS (
    SELECT 
        c.Id,
        c.Name,
        c.ParentId,
        c.CreatedBy,
        ARRAY[c.Name] AS Path,
        1 AS Level,
        CAST(c.Name AS TEXT) AS PathString
    FROM Categories c
    WHERE c.ParentId IS NULL
    
    UNION ALL
    
    SELECT 
        c.Id,
        c.Name,
        c.ParentId,
        c.CreatedBy,
        ct.Path || c.Name,
        ct.Level + 1,
        ct.PathString || ' > ' || c.Name
    FROM Categories c
    INNER JOIN CategoryTree ct ON c.ParentId = ct.Id
)
SELECT 
    ct.*,
    u.FullName as CreatedByFullName
FROM CategoryTree ct
LEFT JOIN Users u ON ct.CreatedBy = u.Id
ORDER BY Path;

-- Представление для статистики документов по категориям
CREATE VIEW DocumentCategoryStats AS
SELECT 
    c.Id as CategoryId,
    c.Name as CategoryName,
    COUNT(DISTINCT dc.DocumentId) as DocumentCount,
    COUNT(DISTINCT ch.Id) as TotalChunks,
    AVG(d.SizeBytes) as AvgDocumentSize
FROM Categories c
LEFT JOIN DocumentCategories dc ON c.Id = dc.CategoryId
LEFT JOIN Documents d ON dc.DocumentId = d.Id
LEFT JOIN Chunks ch ON d.Id = ch.DocumentId
GROUP BY c.Id, c.Name;

-- ============================================
-- 9. Индексы для оптимизации часто используемых запросов
-- ============================================

-- Для поиска документов по имени файла
CREATE INDEX idx_documents_filename_pattern ON Documents(FileName text_pattern_ops);

-- Для поиска по тексту в чанках (если нужно полнотекстовый поиск)
CREATE INDEX idx_chunks_text_trgm ON Chunks USING gin (Text gin_trgm_ops);

-- Для поиска документов по размеру (полезно для отчетов)
CREATE INDEX idx_documents_size_range ON Documents(SizeBytes) WHERE SizeBytes > 0;

-- Составной индекс для часто используемых фильтров документов
CREATE INDEX idx_documents_status_created ON Documents(Status, CreatedAt DESC);

-- ============================================
-- 10. Комментарии к таблицам и полям
-- ============================================
COMMENT ON TABLE Users IS 'Таблица пользователей системы';
COMMENT ON COLUMN Users.Username IS 'Уникальное имя пользователя для входа';
COMMENT ON COLUMN Users.Email IS 'Электронная почта пользователя';
COMMENT ON COLUMN Users.FullName IS 'Полное имя пользователя';

COMMENT ON TABLE Categories IS 'Иерархическая структура категорий документов';
COMMENT ON COLUMN Categories.ParentId IS 'Ссылка на родительскую категорию (NULL для корневых)';

COMMENT ON TABLE Documents IS 'Основная таблица документов';
COMMENT ON COLUMN Documents.Status IS 'Статус документа: draft, processing, active, archived, deleted';

COMMENT ON TABLE DocumentCategories IS 'Связь многие-ко-многим между документами и категориями';

COMMENT ON TABLE Chunks IS 'Текстовые фрагменты документов с векторными представлениями для семантического поиска';
COMMENT ON COLUMN Chunks.Embedding IS 'Векторное представление текста (embedding) размерностью 1536';
COMMENT ON COLUMN Chunks.Metadata IS 'Дополнительные метаданные чанка (страница, заголовок и т.д.) в формате JSON';

-- ============================================
-- 11. Дефолтный пользователь системы (опционально)
-- ============================================
INSERT INTO Users (Id, Username, Email, FullName, IsActive) 
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'system', 'system@localhost', 'System User', true),
    ('00000000-0000-0000-0000-000000000002', 'admin', 'admin@localhost', 'Administrator', true)
ON CONFLICT (Id) DO NOTHING;
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
);

-- Индекс для быстрого поиска пользователей по email
CREATE INDEX idx_users_email ON Users(Email);
CREATE INDEX idx_users_username ON Users(Username);


CREATE TABLE Categories (
    Id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    Name TEXT NOT NULL,
    ParentId UUID,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL
);

-- Внешние ключи для Categories
ALTER TABLE Categories ADD CONSTRAINT fk_parent_category 
    FOREIGN KEY (ParentId) 
    REFERENCES Categories(Id) 
    ON DELETE SET NULL;

ALTER TABLE Categories ADD CONSTRAINT fk_category_createdby 
    FOREIGN KEY (CreatedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

ALTER TABLE Categories ADD CONSTRAINT fk_category_modifiedby 
    FOREIGN KEY (ModifiedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

-- Проверки для Categories
ALTER TABLE Categories ADD CONSTRAINT chk_not_self_parent 
    CHECK (ParentId IS NULL OR ParentId != Id);

-- Уникальность имени в рамках одного уровня иерархии
ALTER TABLE Categories ADD CONSTRAINT uniq_category_name_per_parent 
    UNIQUE (Name, ParentId);

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
    SizeBytes BIGINT NOT NULL,
    Status VARCHAR(50) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL
);

-- Проверки для Documents
ALTER TABLE Documents ADD CONSTRAINT chk_size_non_negative 
    CHECK (SizeBytes >= 0);

ALTER TABLE Documents ADD CONSTRAINT fk_document_createdby 
    FOREIGN KEY (CreatedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

ALTER TABLE Documents ADD CONSTRAINT fk_document_modifiedby 
    FOREIGN KEY (ModifiedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

ALTER TABLE Documents ADD CONSTRAINT chk_valid_status 
    CHECK (Status IN ('draft', 'processing', 'active', 'archived', 'deleted'));

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
    ModifiedBy UUID NOT NULL
);

-- Внешние ключи для DocumentCategories
ALTER TABLE DocumentCategories ADD CONSTRAINT fk_documentcategories_document 
    FOREIGN KEY (DocumentId) 
    REFERENCES Documents(Id) 
    ON DELETE CASCADE;

ALTER TABLE DocumentCategories ADD CONSTRAINT fk_documentcategories_category 
    FOREIGN KEY (CategoryId) 
    REFERENCES Categories(Id) 
    ON DELETE CASCADE;

ALTER TABLE DocumentCategories ADD CONSTRAINT fk_documentcategories_createdby 
    FOREIGN KEY (CreatedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

ALTER TABLE DocumentCategories ADD CONSTRAINT fk_documentcategories_modifiedby 
    FOREIGN KEY (ModifiedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

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
    ChunkIndex INTEGER NOT NULL,
    Text TEXT NOT NULL,
    Embedding vector(1536),
    Metadata JSONB DEFAULT '{}'::jsonb,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CreatedBy UUID NOT NULL,
    ModifiedBy UUID NOT NULL
);

-- Внешние ключи и проверки для Chunks
ALTER TABLE Chunks ADD CONSTRAINT fk_chunks_document 
    FOREIGN KEY (DocumentId) 
    REFERENCES Documents(Id) 
    ON DELETE CASCADE;

ALTER TABLE Chunks ADD CONSTRAINT fk_chunks_createdby 
    FOREIGN KEY (CreatedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

ALTER TABLE Chunks ADD CONSTRAINT fk_chunks_modifiedby 
    FOREIGN KEY (ModifiedBy)
    REFERENCES Users(Id)
    ON DELETE RESTRICT;

ALTER TABLE Chunks ADD CONSTRAINT unique_document_chunk_index 
    UNIQUE (DocumentId, ChunkIndex);

ALTER TABLE Chunks ADD CONSTRAINT chk_chunkindex_non_negative 
    CHECK (ChunkIndex >= 0);

ALTER TABLE Chunks ADD CONSTRAINT chk_text_not_empty 
    CHECK (LENGTH(TRIM(Text)) > 0);

ALTER TABLE Chunks ADD CONSTRAINT chk_max_chunk_size 
    CHECK (LENGTH(Text) <= 10000);

-- Индексы для чанков
CREATE INDEX idx_chunks_documentid ON Chunks(DocumentId);
CREATE INDEX idx_chunks_chunkindex ON Chunks(ChunkIndex);
CREATE INDEX idx_chunks_embedding ON Chunks USING ivfflat (embedding vector_cosine_ops);

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
CREATE INDEX idx_chunks_metadata ON Chunks USING gin (Metadata);
CREATE INDEX idx_chunks_createdby ON Chunks(CreatedBy);
CREATE INDEX idx_chunks_createdat ON Chunks(CreatedAt);
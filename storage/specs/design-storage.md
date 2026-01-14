# CodeGraph MCP Server 스토리지 설계서

**Project**: CodeGraph MCP Server  
**Version**: 1.0.0  
**Created**: 2025-11-26  
**Status**: Draft  
**Document Type**: C4 Model - Component Diagram (Level 3)

---

## 1. 문서 개요

### 1.1 목적

본 문서는 CodeGraph MCP Server의 **스토리지 계층(Storage Layer)** 에 대한 상세 설계를 기술한다.  
코드 그래프 데이터, 캐시, 벡터 데이터를 어떻게 저장·관리·영속화하는지를 명확히 정의하는 것이 목적이다.

### 1.2 범위

- SQLite 기반 그래프 스토리지 설계
- 파일 캐시 설계
- 벡터 스토어 설계
- 데이터 영속화 전략

### 1.3 대상 요구사항

| 요구사항 그룹 | 요구사항 ID | 설명 |
|---------------|-------------|------|
| 스토리지 | REQ-STR-001 ~ REQ-STR-004 | 데이터 영속화 |
| 그래프 엔진 | REQ-GRF-005, REQ-GRF-006 | SQLite / 인덱스 |
| 비기능 | REQ-NFR-005, REQ-NFR-006 | 메모리 / 디스크 |

---

## 2. 스토리지 아키텍처

### 2.1 전체 구성

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Storage Container                                    │
│                         src/codegraph_mcp/storage/                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         Storage Manager                                  ││
│  │                                                                          ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  ││
│  │  │ SQLiteStore  │  │  FileCache   │  │ VectorStore  │                  ││
│  │  │ (Graph Data) │  │ (AST Cache)  │  │ (Embeddings) │                  ││
│  │  │              │  │              │  │              │                  ││
│  │  │ REQ-STR-001  │  │ REQ-STR-002  │  │ REQ-STR-003  │                  ││
│  │  │ REQ-GRF-005  │  │              │  │              │                  ││
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  ││
│  │         │                 │                 │                           ││
│  └─────────┼─────────────────┼─────────────────┼───────────────────────────┘│
│            │                 │                 │                             │
│            ▼                 ▼                 ▼                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         File System                                      ││
│  │                                                                          ││
│  │  ~/.codegraph/                                                          ││
│  │  ├── {repo_hash}/                                                       ││
│  │  │   ├── index.db              ← SQLite Database                       ││
│  │  │   ├── cache/                ← AST Cache                             ││
│  │  │   │   └── {file_hash}.json                                          ││
│  │  │   └── vectors/              ← Vector Store                          ││
│  │  │       └── embeddings.bin                                            ││
│  │  └── config.json               ← Global Config                         ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 디렉터리 구성

```
~/.codegraph/
├── config.json                    # 전역 설정
├── {repo_hash_1}/                 # 리포지토리 1의 데이터
│   ├── index.db                   # SQLite 데이터베이스
│   ├── cache/                     # AST 캐시
│   │   ├── abc123.json            # 파일 해시.json
│   │   └── def456.json
│   ├── vectors/                   # 벡터 스토어
│   │   └── embeddings.bin
│   └── meta.json                  # 리포지토리 메타데이터
│
├── {repo_hash_2}/                 # 리포지토리 2의 데이터
│   └── ...
│
└── logs/                          # 로그 파일
    └── codegraph.log
```

---

## 3. SQLite 스토리지 설계

### 3.1 스키마 정의

```sql
-- storage/schema.sql (REQ-STR-001, REQ-GRF-005)

-- ========================================
-- 엔티티 테이블
-- ========================================
CREATE TABLE IF NOT EXISTS entities (
    -- 기본 키
    id TEXT PRIMARY KEY,
    
    -- 기본 정보
    type TEXT NOT NULL CHECK(type IN (
        'file', 'module', 'class', 'function', 
        'method', 'interface', 'import'
    )),
    name TEXT NOT NULL,
    qualified_name TEXT,
    
    -- 위치 정보
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL CHECK(start_line >= 1),
    end_line INTEGER NOT NULL CHECK(end_line >= start_line),
    
    -- 콘텐츠
    signature TEXT,
    docstring TEXT,
    source_code TEXT,
    
    -- 시맨틱 정보
    embedding BLOB,           -- 벡터 임베딩
    community_id INTEGER,     -- 커뮤니티 ID
    description TEXT,         -- LLM 생성 설명
    
    -- 메타데이터
    language TEXT,
    complexity INTEGER,       -- 순환 복잡도 (옵션)
    
    -- 감사 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 관계 테이블
-- ========================================
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 엔티티 참조
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    
    -- 관계 정보
    type TEXT NOT NULL CHECK(type IN (
        'calls', 'imports', 'inherits', 
        'contains', 'implements', 'uses'
    )),
    weight REAL DEFAULT 1.0 CHECK(weight >= 0),
    
    -- 추가 정보
    metadata TEXT,  -- JSON 형식
    line_number INTEGER,  -- 호출 라인 번호
    
    -- 감사 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 외래 키 제약
    FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
);

-- ========================================
-- 커뮤니티 테이블 (GraphRAG 용)
-- ========================================
CREATE TABLE IF NOT EXISTS communities (
    id INTEGER PRIMARY KEY,
    
    -- 계층 정보
    level INTEGER NOT NULL DEFAULT 0 CHECK(level >= 0),
    parent_id INTEGER,
    
    -- 콘텐츠
    name TEXT,
    summary TEXT,           -- LLM 생성 요약
    
    -- 통계 정보
    member_count INTEGER DEFAULT 0,
    
    -- 감사 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES communities(id) ON DELETE SET NULL
);

-- ========================================
-- 인덱스 정보 테이블
-- ========================================
CREATE TABLE IF NOT EXISTS index_info (
    id INTEGER PRIMARY KEY,
    
    -- 리포지토리 정보
    repo_path TEXT NOT NULL UNIQUE,
    repo_name TEXT,
    
    -- Git 정보
    last_commit TEXT,
    branch TEXT,
    
    -- 통계 정보
    total_files INTEGER DEFAULT 0,
    total_entities INTEGER DEFAULT 0,
    total_relations INTEGER DEFAULT 0,
    
    -- 타이밍 정보
    last_indexed_at TIMESTAMP,
    index_duration_ms REAL,
    
    -- 감사 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 파일 상태 테이블 (증분 인덱싱용)
-- ========================================
CREATE TABLE IF NOT EXISTS file_states (
    file_path TEXT PRIMARY KEY,
    
    -- 파일 정보
    content_hash TEXT NOT NULL,     -- 파일 내용 해시
    size_bytes INTEGER,
    
    -- 상태
    last_modified TIMESTAMP,
    last_indexed_at TIMESTAMP,
    
    -- 분석 결과
    entity_count INTEGER DEFAULT 0,
    relation_count INTEGER DEFAULT 0,
    parse_errors TEXT,              -- JSON 배열
    
    -- 감사 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 인덱스 정의 (REQ-GRF-006)
-- ========================================

-- 엔티티 인덱스
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_file ON entities(file_path);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_qualified ON entities(qualified_name);
CREATE INDEX IF NOT EXISTS idx_entities_community ON entities(community_id);
CREATE INDEX IF NOT EXISTS idx_entities_language ON entities(language);

-- 관계 인덱스
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type);

-- 복합 인덱스 (쿼리 최적화용)
CREATE INDEX IF NOT EXISTS idx_relations_src_type ON relations(source_id, type);
CREATE INDEX IF NOT EXISTS idx_relations_tgt_type ON relations(target_id, type);
CREATE INDEX IF NOT EXISTS idx_entities_file_type ON entities(file_path, type);

-- 커뮤니티 인덱스
CREATE INDEX IF NOT EXISTS idx_communities_level ON communities(level);
CREATE INDEX IF NOT EXISTS idx_communities_parent ON communities(parent_id);

-- 파일 상태 인덱스
CREATE INDEX IF NOT EXISTS idx_file_states_hash ON file_states(content_hash);

-- ========================================
-- 트리거 정의
-- ========================================

-- 엔티티 업데이트 시 updated_at 갱신
CREATE TRIGGER IF NOT EXISTS update_entity_timestamp
AFTER UPDATE ON entities
BEGIN
    UPDATE entities SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- 커뮤니티 업데이트 시 updated_at 갱신
CREATE TRIGGER IF NOT EXISTS update_community_timestamp
AFTER UPDATE ON communities
BEGIN
    UPDATE communities SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- 파일 상태 업데이트 시 updated_at 갱신
CREATE TRIGGER IF NOT EXISTS update_file_state_timestamp
AFTER UPDATE ON file_states
BEGIN
    UPDATE file_states SET updated_at = CURRENT_TIMESTAMP 
    WHERE file_path = NEW.file_path;
END;
```

### 3.2 SQLite 스토어 클래스

```python
# storage/sqlite.py

import aiosqlite
from pathlib import Path
from typing import Optional, AsyncIterator
from contextlib import asynccontextmanager

class SQLiteStore:
    """SQLite 기반 그래프 스토리지 (REQ-STR-001)"""
    
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """데이터베이스에 연결"""
        # 디렉터리 생성
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 연결
        self._connection = await aiosqlite.connect(
            self._db_path,
            isolation_level=None  # autocommit
        )
        
        # 설정
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA synchronous=NORMAL")
        await self._connection.execute("PRAGMA cache_size=10000")
        await self._connection.execute("PRAGMA temp_store=MEMORY")
        
        # 스키마 초기화
        await self._init_schema()
    
    async def close(self) -> None:
        """연결 종료"""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def _init_schema(self) -> None:
        """스키마 초기화"""
        schema_path = Path(__file__).parent / "schema.sql"
        schema = schema_path.read_text()
        await self._connection.executescript(schema)
    
    # ========================================
    # 엔티티 조작
    # ========================================
    
    async def add_entity(self, entity: Entity) -> str:
        """엔티티 추가"""
        sql = """
            INSERT OR REPLACE INTO entities (
                id, type, name, qualified_name,
                file_path, start_line, end_line,
                signature, docstring, source_code,
                embedding, community_id, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self._connection.execute(sql, (
            entity.id,
            entity.type.value,
            entity.name,
            entity.qualified_name,
            entity.file_path,
            entity.start_line,
            entity.end_line,
            entity.signature,
            entity.docstring,
            entity.source_code,
            entity.embedding,
            entity.community_id,
            self._detect_language(entity.file_path)
        ))
        return entity.id
    
    async def add_entities_batch(
        self, 
        entities: list[Entity]
    ) -> int:
        """엔티티 일괄 추가 (성능 최적화)"""
        sql = """
            INSERT OR REPLACE INTO entities (
                id, type, name, qualified_name,
                file_path, start_line, end_line,
                signature, docstring, source_code,
                embedding, community_id, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        data = [
            (
                e.id, e.type.value, e.name, e.qualified_name,
                e.file_path, e.start_line, e.end_line,
                e.signature, e.docstring, e.source_code,
                e.embedding, e.community_id,
                self._detect_language(e.file_path)
            )
            for e in entities
        ]
        await self._connection.executemany(sql, data)
        return len(entities)
    
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """엔티티 조회"""
        sql = "SELECT * FROM entities WHERE id = ?"
        async with self._connection.execute(sql, (entity_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_entity(row)
        return None
    
    async def get_entity_by_name(
        self, 
        name: str, 
        entity_type: str = None
    ) -> Optional[Entity]:
        """이름으로 엔티티 조회"""
        if entity_type:
            sql = """
                SELECT * FROM entities 
                WHERE (name = ? OR qualified_name = ?) AND type = ?
            """
            params = (name, name, entity_type)
        else:
            sql = """
                SELECT * FROM entities 
                WHERE name = ? OR qualified_name = ?
            """
            params = (name, name)
        
        async with self._connection.execute(sql, params) as cursor:
            row = await cursor.fetchone()
            if row:
                return self._row_to_entity(row)
        return None
    
    async def get_entities_by_file(
        self, 
        file_path: str
    ) -> list[Entity]:
        """파일 내 엔티티 조회"""
        sql = """
            SELECT * FROM entities 
            WHERE file_path = ?
            ORDER BY start_line
        """
        async with self._connection.execute(sql, (file_path,)) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    async def search_entities(
        self,
        query: str,
        entity_types: list[str] = None,
        limit: int = 100
    ) -> list[Entity]:
        """엔티티 검색"""
        conditions = ["(name LIKE ? OR qualified_name LIKE ? OR docstring LIKE ?)"]
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if entity_types:
            placeholders = ','.join('?' * len(entity_types))
            conditions.append(f"type IN ({placeholders})")
            params.extend(entity_types)
        
        sql = f"""
            SELECT * FROM entities 
            WHERE {' AND '.join(conditions)}
            LIMIT ?
        """
        params.append(limit)
        
        async with self._connection.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    async def delete_entities_by_file(self, file_path: str) -> int:
        """파일 단위 엔티티 삭제"""
        # 먼저 관계 삭제
        await self._connection.execute("""
            DELETE FROM relations 
            WHERE source_id IN (SELECT id FROM entities WHERE file_path = ?)
               OR target_id IN (SELECT id FROM entities WHERE file_path = ?)
        """, (file_path, file_path))
        
        # 엔티티 삭제
        cursor = await self._connection.execute(
            "DELETE FROM entities WHERE file_path = ?",
            (file_path,)
        )
        return cursor.rowcount
    
    # ========================================
    # 관계 조작
    # ========================================
    
    async def add_relation(self, relation: Relation) -> int:
        """관계 추가"""
        sql = """
            INSERT INTO relations (
                source_id, target_id, type, weight, metadata, line_number
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = await self._connection.execute(sql, (
            relation.source_id,
            relation.target_id,
            relation.type.value,
            relation.weight,
            json.dumps(relation.metadata) if relation.metadata else None,
            relation.line_number
        ))
        return cursor.lastrowid
    
    async def add_relations_batch(
        self, 
        relations: list[Relation]
    ) -> int:
        """관계 일괄 추가"""
        sql = """
            INSERT INTO relations (
                source_id, target_id, type, weight, metadata, line_number
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        data = [
            (
                r.source_id, r.target_id, r.type.value, r.weight,
                json.dumps(r.metadata) if r.metadata else None,
                r.line_number
            )
            for r in relations
        ]
        await self._connection.executemany(sql, data)
        return len(relations)
    
    async def get_relations_by_source(
        self,
        source_id: str,
        relation_types: list[str] = None
    ) -> list[Relation]:
        """소스 ID 기준 관계 조회"""
        if relation_types:
            placeholders = ','.join('?' * len(relation_types))
            sql = f"""
                SELECT * FROM relations 
                WHERE source_id = ? AND type IN ({placeholders})
            """
            params = [source_id] + relation_types
        else:
            sql = "SELECT * FROM relations WHERE source_id = ?"
            params = [source_id]
        
        async with self._connection.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_relation(row) for row in rows]
    
    async def get_relations_by_target(
        self,
        target_id: str,
        relation_types: list[str] = None
    ) -> list[Relation]:
        """타깃 ID 기준 관계 조회"""
        if relation_types:
            placeholders = ','.join('?' * len(relation_types))
            sql = f"""
                SELECT * FROM relations 
                WHERE target_id = ? AND type IN ({placeholders})
            """
            params = [target_id] + relation_types
        else:
            sql = "SELECT * FROM relations WHERE target_id = ?"
            params = [target_id]
        
        async with self._connection.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_relation(row) for row in rows]
    
    # ========================================
    # 통계 및 메타 정보
    # ========================================
    
    async def get_stats(self) -> GraphStats:
        """통계 정보 조회"""
        # 엔티티 수
        async with self._connection.execute(
            "SELECT COUNT(*) FROM entities"
        ) as cursor:
            total_entities = (await cursor.fetchone())[0]
        
        # 관계 수
        async with self._connection.execute(
            "SELECT COUNT(*) FROM relations"
        ) as cursor:
            total_relations = (await cursor.fetchone())[0]
        
        # 엔티티 유형별 내역
        async with self._connection.execute(
            "SELECT type, COUNT(*) FROM entities GROUP BY type"
        ) as cursor:
            entity_breakdown = dict(await cursor.fetchall())
        
        # 언어별 내역
        async with self._connection.execute(
            "SELECT language, COUNT(*) FROM entities GROUP BY language"
        ) as cursor:
            language_breakdown = dict(await cursor.fetchall())
        
        # 파일 수
        async with self._connection.execute(
            "SELECT COUNT(DISTINCT file_path) FROM entities"
        ) as cursor:
            total_files = (await cursor.fetchone())[0]
        
        # 인덱스 정보
        async with self._connection.execute(
            "SELECT last_indexed_at, index_duration_ms FROM index_info LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
            last_indexed_at = row[0] if row else None
            index_duration_ms = row[1] if row else 0
        
        return GraphStats(
            total_files=total_files,
            total_entities=total_entities,
            total_relations=total_relations,
            entity_breakdown=entity_breakdown,
            language_breakdown=language_breakdown,
            last_indexed_at=last_indexed_at,
            index_duration_ms=index_duration_ms
        )
```

---

## 4. 파일 캐시 설계

### 4.1 캐시 구조

```python
# storage/cache.py (REQ-STR-002)

import hashlib
import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict

@dataclass
class CacheEntry:
    """캐시 엔트리"""
    file_path: str
    content_hash: str
    language: str
    entities: list[dict]
    relations: list[dict]
    parse_errors: list[str]
    cached_at: str

class FileCache:
    """파일 캐시 매니저"""
    
    def __init__(self, cache_dir: str):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, file_path: str) -> Path:
        """캐시 파일 경로 조회"""
        # 파일 경로 해시를 캐시 키로 사용
        path_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self._cache_dir / f"{path_hash}.json"
    
    def _compute_content_hash(self, content: str) -> str:
        """콘텐츠 해시 계산"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get(
        self, 
        file_path: str, 
        content: str
    ) -> Optional[CacheEntry]:
        """캐시 조회"""
        cache_path = self._get_cache_path(file_path)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            entry = CacheEntry(**data)
            
            # 콘텐츠 해시 검증
            current_hash = self._compute_content_hash(content)
            if entry.content_hash != current_hash:
                # 파일이 변경됨
                return None
            
            return entry
            
        except (json.JSONDecodeError, TypeError, KeyError):
            # 캐시 손상
            cache_path.unlink(missing_ok=True)
            return None
    
    async def set(
        self,
        file_path: str,
        content: str,
        language: str,
        entities: list[Entity],
        relations: list[Relation],
        parse_errors: list[str]
    ) -> None:
        """캐시 저장"""
        cache_path = self._get_cache_path(file_path)
        
        entry = CacheEntry(
            file_path=file_path,
            content_hash=self._compute_content_hash(content),
            language=language,
            entities=[asdict(e) for e in entities],
            relations=[asdict(r) for r in relations],
            parse_errors=parse_errors,
            cached_at=datetime.utcnow().isoformat()
        )
        
        with open(cache_path, 'w') as f:
            json.dump(asdict(entry), f, indent=2)
    
    async def invalidate(self, file_path: str) -> None:
        """캐시 무효화"""
        cache_path = self._get_cache_path(file_path)
        cache_path.unlink(missing_ok=True)
    
    async def clear(self) -> int:
        """전체 캐시 삭제"""
        count = 0
        for cache_file in self._cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count
    
    async def get_cache_stats(self) -> dict:
        """캐시 통계 조회"""
        cache_files = list(self._cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "entry_count": len(cache_files),
            "total_size_bytes": total_size,
            "cache_dir": str(self._cache_dir)
        }
```

---

## 5. 벡터 스토어 설계

### 5.1 벡터 스토어 구조

```python
# storage/vectors.py (REQ-STR-003)

import numpy as np
from pathlib import Path
from typing import Optional
import struct

class VectorStore:
    """벡터 스토어(임베딩 관리)"""
    
    VECTOR_DIM = 384  # sentence-transformers default
    
    def __init__(self, store_path: str):
        self._store_path = Path(store_path)
        self._store_path.mkdir(parents=True, exist_ok=True)
        
        self._embeddings_file = self._store_path / "embeddings.bin"
        self._index_file = self._store_path / "index.json"
        
        self._id_to_offset: dict[str, int] = {}
        self._embeddings: Optional[np.memmap] = None
        
        self._load_index()
    
    def _load_index(self) -> None:
        """인덱스 로드"""
        if self._index_file.exists():
            with open(self._index_file, 'r') as f:
                self._id_to_offset = json.load(f)
    
    def _save_index(self) -> None:
        """인덱스 저장"""
        with open(self._index_file, 'w') as f:
            json.dump(self._id_to_offset, f)
    
    async def add(
        self, 
        entity_id: str, 
        embedding: np.ndarray
    ) -> None:
        """임베딩 추가"""
        if embedding.shape[0] != self.VECTOR_DIM:
            raise ValueError(
                f"Invalid embedding dimension: {embedding.shape[0]}, "
                f"expected {self.VECTOR_DIM}"
            )
        
        # 파일에 append
        offset = 0
        if self._embeddings_file.exists():
            offset = self._embeddings_file.stat().st_size // (self.VECTOR_DIM * 4)
        
        with open(self._embeddings_file, 'ab') as f:
            f.write(embedding.astype(np.float32).tobytes())
        
        # 인덱스 갱신
        self._id_to_offset[entity_id] = offset
        self._save_index()
    
    async def add_batch(
        self, 
        embeddings: dict[str, np.ndarray]
    ) -> int:
        """임베딩 일괄 추가"""
        if not embeddings:
            return 0
        
        offset = 0
        if self._embeddings_file.exists():
            offset = self._embeddings_file.stat().st_size // (self.VECTOR_DIM * 4)
        
        with open(self._embeddings_file, 'ab') as f:
            for entity_id, embedding in embeddings.items():
                if embedding.shape[0] != self.VECTOR_DIM:
                    continue
                
                f.write(embedding.astype(np.float32).tobytes())
                self._id_to_offset[entity_id] = offset
                offset += 1
        
        self._save_index()
        return len(embeddings)
    
    async def get(self, entity_id: str) -> Optional[np.ndarray]:
        """임베딩 조회"""
        if entity_id not in self._id_to_offset:
            return None
        
        offset = self._id_to_offset[entity_id]
        
        with open(self._embeddings_file, 'rb') as f:
            f.seek(offset * self.VECTOR_DIM * 4)
            data = f.read(self.VECTOR_DIM * 4)
            return np.frombuffer(data, dtype=np.float32)
    
    async def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        entity_ids: list[str] = None
    ) -> list[tuple[str, float]]:
        """유사 벡터 검색"""
        if not self._embeddings_file.exists():
            return []
        
        # 전체 임베딩 로드
        embeddings = np.memmap(
            self._embeddings_file,
            dtype=np.float32,
            mode='r',
            shape=(len(self._id_to_offset), self.VECTOR_DIM)
        )
        
        # 코사인 유사도 계산
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        similarities = np.dot(embeddings_norm, query_norm)
        
        # 필터링(지정 ID만)
        if entity_ids:
            mask = np.zeros(len(self._id_to_offset), dtype=bool)
            id_list = list(self._id_to_offset.keys())
            for i, eid in enumerate(id_list):
                if eid in entity_ids:
                    mask[i] = True
            similarities = np.where(mask, similarities, -1)
        
        # Top-K 추출
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        id_list = list(self._id_to_offset.keys())
        results = [
            (id_list[i], float(similarities[i]))
            for i in top_indices
            if similarities[i] > 0
        ]
        
        return results
    
    async def delete(self, entity_id: str) -> bool:
        """임베딩 삭제(논리 삭제)"""
        if entity_id in self._id_to_offset:
            del self._id_to_offset[entity_id]
            self._save_index()
            return True
        return False
    
    async def rebuild(self) -> None:
        """벡터 스토어 재구축(논리 삭제 반영)"""
        if not self._embeddings_file.exists():
            return
        
        # 유효 엔트리만 새 파일로 재작성
        new_file = self._store_path / "embeddings_new.bin"
        new_offsets = {}
        
        with open(new_file, 'wb') as f_out:
            with open(self._embeddings_file, 'rb') as f_in:
                offset = 0
                for entity_id, old_offset in self._id_to_offset.items():
                    f_in.seek(old_offset * self.VECTOR_DIM * 4)
                    data = f_in.read(self.VECTOR_DIM * 4)
                    f_out.write(data)
                    new_offsets[entity_id] = offset
                    offset += 1
        
        # 파일 교체
        self._embeddings_file.unlink()
        new_file.rename(self._embeddings_file)
        
        self._id_to_offset = new_offsets
        self._save_index()
```

---

## 6. 스토리지 매니저 설계

### 6.1 통합 매니저

```python
# storage/__init__.py

from pathlib import Path
import hashlib

class StorageManager:
    """스토리지 통합 매니저"""
    
    def __init__(self, base_dir: str = None):
        self._base_dir = Path(base_dir or Path.home() / ".codegraph")
        self._base_dir.mkdir(parents=True, exist_ok=True)
        
        self._stores: dict[str, tuple[SQLiteStore, FileCache, VectorStore]] = {}
    
    def _get_repo_hash(self, repo_path: str) -> str:
        """리포지토리 경로 해시 조회"""
        return hashlib.md5(repo_path.encode()).hexdigest()[:12]
    
    def _get_repo_dir(self, repo_path: str) -> Path:
        """리포지토리 스토리지 디렉터리 조회"""
        repo_hash = self._get_repo_hash(repo_path)
        return self._base_dir / repo_hash
    
    async def get_stores(
        self, 
        repo_path: str
    ) -> tuple[SQLiteStore, FileCache, VectorStore]:
        """리포지토리 스토어 조회"""
        if repo_path in self._stores:
            return self._stores[repo_path]
        
        repo_dir = self._get_repo_dir(repo_path)
        repo_dir.mkdir(parents=True, exist_ok=True)
        
        # 각 스토어 초기화
        sqlite_store = SQLiteStore(str(repo_dir / "index.db"))
        await sqlite_store.connect()
        
        file_cache = FileCache(str(repo_dir / "cache"))
        vector_store = VectorStore(str(repo_dir / "vectors"))
        
        # 메타데이터 저장
        await self._save_repo_meta(repo_dir, repo_path)
        
        stores = (sqlite_store, file_cache, vector_store)
        self._stores[repo_path] = stores
        
        return stores
    
    async def _save_repo_meta(self, repo_dir: Path, repo_path: str) -> None:
        """리포지토리 메타데이터 저장"""
        meta_file = repo_dir / "meta.json"
        meta = {
            "repo_path": repo_path,
            "created_at": datetime.utcnow().isoformat()
        }
        with open(meta_file, 'w') as f:
            json.dump(meta, f, indent=2)
    
    async def list_repositories(self) -> list[dict]:
        """관리 중인 리포지토리 목록 조회"""
        repos = []
        for repo_dir in self._base_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            
            meta_file = repo_dir / "meta.json"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    meta = json.load(f)
                    repos.append(meta)
        
        return repos
    
    async def delete_repository(self, repo_path: str) -> bool:
        """리포지토리 스토리지 삭제"""
        repo_dir = self._get_repo_dir(repo_path)
        
        if not repo_dir.exists():
            return False
        
        # 연결 종료
        if repo_path in self._stores:
            sqlite_store, _, _ = self._stores[repo_path]
            await sqlite_store.close()
            del self._stores[repo_path]
        
        # 디렉터리 삭제
        import shutil
        shutil.rmtree(repo_dir)
        
        return True
    
    async def close_all(self) -> None:
        """모든 연결 종료"""
        for repo_path, (sqlite_store, _, _) in self._stores.items():
            await sqlite_store.close()
        self._stores.clear()
```

---

## 7. 데이터 정합성

### 7.1 트랜잭션 관리

```python
# storage/transaction.py

from contextlib import asynccontextmanager

class TransactionManager:
    """트랜잭션 매니저"""
    
    def __init__(self, sqlite_store: SQLiteStore):
        self._store = sqlite_store
    
    @asynccontextmanager
    async def transaction(self):
        """트랜잭션 컨텍스트"""
        conn = self._store._connection
        
        await conn.execute("BEGIN TRANSACTION")
        try:
            yield
            await conn.execute("COMMIT")
        except Exception:
            await conn.execute("ROLLBACK")
            raise
    
    async def batch_update(
        self,
        entities: list[Entity],
        relations: list[Relation]
    ) -> None:
        """배치 업데이트(트랜잭션 내에서 실행)"""
        async with self.transaction():
            await self._store.add_entities_batch(entities)
            await self._store.add_relations_batch(relations)
```

### 7.2 백업·복구

```python
# storage/backup.py

import shutil
from datetime import datetime

class BackupManager:
    """백업 매니저"""
    
    def __init__(self, storage_manager: StorageManager):
        self._storage = storage_manager
    
    async def create_backup(self, repo_path: str) -> str:
        """백업 생성"""
        repo_dir = self._storage._get_repo_dir(repo_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = repo_dir.parent / f"{repo_dir.name}_backup_{timestamp}"
        
        shutil.copytree(repo_dir, backup_dir)
        
        return str(backup_dir)
    
    async def restore_backup(
        self, 
        repo_path: str, 
        backup_path: str
    ) -> bool:
        """백업에서 복구 (REQ-NFR-008)"""
        repo_dir = self._storage._get_repo_dir(repo_path)
        backup_dir = Path(backup_path)
        
        if not backup_dir.exists():
            return False
        
        # 현재 디렉터리 삭제
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        
        # 백업에서 복사
        shutil.copytree(backup_dir, repo_dir)
        
        return True
    
    async def list_backups(self, repo_path: str) -> list[str]:
        """백업 목록 조회"""
        repo_dir = self._storage._get_repo_dir(repo_path)
        base_name = repo_dir.name
        
        backups = []
        for d in repo_dir.parent.iterdir():
            if d.is_dir() and d.name.startswith(f"{base_name}_backup_"):
                backups.append(str(d))
        
        return sorted(backups, reverse=True)
```

---

## 8. 성능 최적화

### 8.1 최적화 전략

| 전략     | 설명          | 대상 요구사항     |
| ------ | ----------- | ----------- |
| WAL 모드 | 쓰기 성능 향상    | REQ-NFR-001 |
| 배치 삽입  | 일괄 삽입으로 고속화 | REQ-NFR-001 |
| 인덱스    | 쿼리 고속화      | REQ-NFR-003 |
| 커넥션 풀  | 연결 재사용      | REQ-NFR-003 |
| 캐시     | 파싱 결과 재사용   | REQ-NFR-002 |

### 8.2 메모리 관리

```python
# storage/memory.py (REQ-NFR-005)

class MemoryManager:
    """메모리 관리"""
    
    MAX_CACHE_SIZE_MB = 100
    MAX_BATCH_SIZE = 1000
    
    def __init__(self, file_cache: FileCache):
        self._cache = file_cache
    
    async def enforce_limits(self) -> None:
        """메모리 제한 강제"""
        stats = await self._cache.get_cache_stats()
        
        if stats["total_size_bytes"] > self.MAX_CACHE_SIZE_MB * 1024 * 1024:
            # 오래된 캐시 삭제
            await self._evict_old_entries()
    
    async def _evict_old_entries(self) -> None:
        """오래된 엔트리 삭제(LRU)"""
        # 구현 생략
        pass
```

---

## 9. 요구사항 트레이서빌리티

### 9.1 컴포넌트 → 요구사항 매핑

| 컴포넌트           | 파일                  | 요구사항 ID                               | Phase |
| -------------- | ------------------- | ------------------------------------- | ----- |
| SQLiteStore    | storage/sqlite.py   | REQ-STR-001, REQ-GRF-005, REQ-GRF-006 | P0    |
| FileCache      | storage/cache.py    | REQ-STR-002                           | P0    |
| VectorStore    | storage/vectors.py  | REQ-STR-003                           | P1    |
| StorageManager | storage/**init**.py | REQ-STR-001~003                       | P0    |
| BackupManager  | storage/backup.py   | REQ-NFR-008                           | P0    |
| MemoryManager  | storage/memory.py   | REQ-NFR-005                           | P0    |

---

## 10. 변경 이력

| 버전    | 날짜         | 변경 내용 | 작성자    |
| ----- | ---------- | ----- | ------ |
| 1.0.0 | 2025-11-26 | 초판 작성 | System |

---

**문서 상태**: Draft  
**헌법 준수 여부**: Article I (Library-First), Article VIII (No Abstraction) ✓

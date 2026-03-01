# Architecture Overview

## Design Philosophy

PerDocMan is intentionally local-first. All ingestion, indexing, and
retrieval occur on the user's machine. The system prioritizes privacy,
data sovereignty, and extensibility over feature complexity.

Core architectural principles:

-   Local data control
-   Minimal external dependencies
-   Defensive programming
-   Extensible schema design
-   Graceful failure handling

------------------------------------------------------------------------

## System Components

### 1. Web Server Layer

-   Implemented using `BaseHTTPRequestHandler`
-   Handles routing for:
    -   Dashboard (`/`)
    -   Document list (`/documents`)
    -   Document preview (`/doc?id=...`)
    -   Ingestion (`/ingest`)
    -   Reset (`/reset`)

### 2. Database Layer

-   SQLite file-based database
-   Schema created and verified via `init_db()`
-   Defensive migration logic using `PRAGMA table_info`
-   Tables:
    -   `documents`
    -   `sessions`

### 3. Ingestion Pipeline

Document ingestion flow:

1.  User uploads PDF
2.  Temporary file created
3.  SHA-256 hash computed
4.  Duplicate check performed
5.  File copied to managed storage
6.  Preview text extracted (first pages)
7.  Metadata inserted into SQLite
8.  User redirected to dashboard

------------------------------------------------------------------------

## Database Schema

### documents

-   id (INTEGER PRIMARY KEY)
-   original_filename (TEXT)
-   stored_path (TEXT)
-   sha256 (TEXT)
-   category (TEXT)
-   tags (TEXT)
-   doc_date (TEXT)
-   ingested_at (TEXT)
-   content_preview (TEXT)

The `content_preview` column supports future semantic indexing.

### sessions

-   session_id (TEXT PRIMARY KEY)
-   started_at (TEXT)
-   ended_at (TEXT)
-   username (TEXT)
-   hostname (TEXT)
-   vault_root (TEXT)
-   notes (TEXT)

------------------------------------------------------------------------

## Reset Strategy

Due to Windows file locking, the database reset performs a logical wipe:

-   `DELETE FROM documents`
-   `DELETE FROM sessions`

The schema remains intact to ensure stability during runtime.

------------------------------------------------------------------------

## Security Considerations

-   Duplicate prevention via SHA-256 hashing
-   Inline PDF serving restricted to stored DB records
-   No external API exposure
-   No cloud storage integration
-   Prototype assumes trusted local environment

------------------------------------------------------------------------

## Future Architectural Enhancements

-   Semantic search via embedding vectors
-   Vector table integration
-   Role-based authentication
-   Encryption-at-rest
-   REST API abstraction layer
-   Modular front-end separation

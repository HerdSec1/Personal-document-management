# PerDocMan (Personal Document Manager)

PerDocMan is a local-first prototype document management system built in
Python using SQLite. It ingests PDF documents, stores metadata, and
provides retrieval and preview functionality --- all without cloud
services.

This project was developed as a senior seminar capstone focused on
secure, privacy-preserving document indexing and extensible architecture
for future semantic search integration.

------------------------------------------------------------------------

## Features

### Core Functionality

-   PDF ingestion via web interface
-   Local storage of files in managed directory
-   Metadata persistence using SQLite
-   SHA-256 hashing for duplicate detection
-   Automatic duplicate prevention
-   Document listing dashboard
-   Inline PDF preview in browser
-   Session tracking for audit purposes

### Administrative Controls

-   Logical database wipe (documents + sessions cleared)
-   Confirmation prompt for destructive operations
-   Graceful recovery after reset

### Architecture Enhancements

-   `content_preview` column for semantic-ready indexing
-   Schema migration logic using `PRAGMA table_info`
-   Defensive database initialization (`init_db()` safeguards)

------------------------------------------------------------------------

## System Architecture

-   Language: Python 3.11+
-   Web Server: BaseHTTPRequestHandler
-   Database: SQLite (local file-based)
-   Storage: Local filesystem (`data/documents/`)
-   Hashing: SHA-256
-   PDF Parsing: pypdf

All operations are local. No external APIs or cloud services are used.

------------------------------------------------------------------------

## Project Structure

src/ │ ├── launcher.py ├── perdocman_server.py ├── db.py ├── ingest.py
├── reset_db.py └── config.py │ data/ ├── documents.db └── documents/

------------------------------------------------------------------------

## Running the Application

Activate your virtual environment:

    .\.venv\Scripts\activate

Run the server:

    .\.venv\Scripts\python.exe -m src.launcher

Then open:

    http://127.0.0.1:<PORT>/

------------------------------------------------------------------------

## Resetting the Database

Use the **Wipe Database** button on the dashboard.

This performs a logical wipe: - Deletes all document records - Deletes
all session records - Leaves schema intact - Avoids Windows file-lock
issues

------------------------------------------------------------------------

## Current Limitations

-   No authentication (local prototype only)
-   No role-based permissions
-   No full-text or semantic search yet
-   No individual document delete
-   No encryption-at-rest

------------------------------------------------------------------------

## Future Enhancements

-   Embedding-based semantic search
-   Vector storage extension table
-   Individual document deletion
-   Authentication layer
-   Encrypted vault storage
-   Tag-based filtering and search
-   REST API abstraction layer

------------------------------------------------------------------------

## Educational Objectives

This project demonstrates:

-   Secure local-first design principles
-   Defensive schema initialization
-   Duplicate prevention via cryptographic hashing
-   Safe destructive operation handling
-   Extensible architecture for semantic search

------------------------------------------------------------------------

## License

Prototype -- Educational Use Only

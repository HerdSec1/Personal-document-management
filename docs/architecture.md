# System Architecture

## Overview

PerDocMan.exe is a local-first personal document management prototype designed to run entirely on a single user’s Windows machine. The system provides a local web-based interface for ingesting, indexing, and retrieving personal PDF documents while minimizing external exposure and maintaining transparency in data handling.

The application operates only while the executable is running. No background services, cloud dependencies, or persistent network listeners are used.

---

## High-Level Components

The system is composed of the following logical components:

### 1. Executable Launcher (PerDocMan.exe)
- Entry point for the user
- Starts the local HTTP server
- Opens the default web browser to the local interface
- Terminates the server and records a session audit entry on exit

### 2. Local HTTP Server
- Implemented using Python’s standard library
- Bound explicitly to `127.0.0.1`
- Serves HTML pages for interaction with the system
- Handles document ingestion, listing, and search requests

### 3. Metadata Store (SQLite)
- Stores structured metadata about ingested documents
- Maintains indexes to support efficient retrieval
- Stores integrity indicators and audit/session data

### 4. Document Vault
- A local directory under the user’s profile
- Contains managed copies of ingested PDF files
- Access is governed by the operating system’s file permissions

---

## Runtime Lifecycle

1. User launches **PerDocMan.exe**
2. The executable:
   - Initializes runtime configuration
   - Starts the local HTTP server on a random available port
   - Opens the browser to `http://127.0.0.1:<port>/`
3. User interacts with the local web interface
4. On application exit:
   - The HTTP server is shut down
   - Database and file handles are closed
   - Session end time and user information are recorded

---

## Data Flow Summary

- PDF files are ingested through the local interface
- Files are copied into the managed vault directory
- Metadata and integrity data are recorded in SQLite
- Search requests are translated into SQL queries
- Results are rendered as local HTML pages

---

## Design Constraints

- Single-user, single-machine operation
- Local-only network access
- Prototype-level UI and security controls
- No reliance on external services or APIs

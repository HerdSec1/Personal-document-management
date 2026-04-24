# Data Integrity

## Overview

PerDocMan implements a set of controls designed to maintain the consistency, accuracy, and reliability of stored documents and their associated metadata. As a local-first system, data integrity is critical to ensuring that documents remain trustworthy and retrievable over time.

Rather than relying on external systems, integrity is maintained through controlled ingestion, hashing, and database-backed validation.

---

## Integrity Design Principles

The system follows several key principles:

- Single source of truth (SQLite database)
- Controlled ingestion pipeline
- Deterministic file storage
- Detectable (but not enforced) integrity validation
- Graceful handling of inconsistencies

---

## Controlled Ingestion Pipeline

All documents enter the system through a structured ingestion workflow:

1. User uploads a PDF file
2. File is written to a temporary location
3. SHA-256 hash is computed
4. Duplicate check is performed
5. File is copied into managed storage
6. Metadata is inserted into the database
7. Temporary files are cleaned up

This ensures that:

- Files are not partially written into storage
- Duplicate records are prevented before insertion
- Every stored file has a corresponding database record

---

## Duplicate Detection (SHA-256 Hashing)

Each document is hashed using the SHA-256 algorithm during ingestion.

- The hash is computed from the file contents
- The system checks for existing records with the same hash
- Duplicate documents are rejected before being stored

### Purpose

- Prevents redundant storage
- Ensures each document is uniquely identified by its content
- Enables future integrity validation workflows

---

## Metadata as Source of Truth

The SQLite database acts as the authoritative record of all documents.

Each document entry includes:

- Stored file path
- Original filename
- Hash value
- Metadata (category, tags, dates)
- Sensitivity classification
- Preview content

All application operations reference the database rather than directly scanning the file system.

### Integrity Benefit

- Prevents orphaned files from being treated as valid documents
- Ensures consistent retrieval and indexing behavior

---

## File-System Consistency Checks

When a document is accessed:

- The system retrieves the file path from the database
- The file system is checked to confirm the file exists

If a mismatch occurs:

- The system returns an error instead of attempting recovery
- The inconsistency is surfaced to the user

### Purpose

- Avoids silent failures
- Prevents incorrect or missing data from being served

---

## Reset Strategy

The system includes a controlled reset mechanism:

- All document records are deleted from the database
- All stored PDF files are removed from the storage directory
- The database schema remains intact

This approach avoids:

- File locking issues (especially on Windows)
- Schema corruption
- Partial resets

---

## Preview Extraction and Metadata Enrichment

During ingestion:

- Text is extracted from the first pages of the document
- A preview is stored in the database
- A display title is derived from content when possible

### Integrity Consideration

- Extracted content is supplemental and does not replace the original document
- Failures in extraction do not impact core document storage

---

## Integrity Limitations

As a prototype system, the following limitations exist:

- Hashes are not revalidated automatically after ingestion
- No background process monitors file changes
- No enforcement mechanism prevents manual file modification outside the application
- No cryptographic signing or tamper-proof storage

Integrity is therefore **detectable but not enforced**.

---

## Future Enhancements

Potential improvements include:

- Periodic hash revalidation to detect file tampering
- Automated integrity checks during system startup
- Alerting mechanisms for mismatched files
- Cryptographic signing of stored documents
- Versioning or snapshot support for document history

---

## Integrity Perspective

PerDocMan demonstrates how data integrity can be maintained in a local-first system through:

- Controlled data entry (ingestion pipeline)
- Deterministic storage
- Database-backed indexing
- Hash-based identification

These mechanisms ensure that documents remain consistent, traceable, and reliably accessible within the scope of the prototype.
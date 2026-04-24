# Version History

## Overview

PerDocMan was developed using an iterative, milestone-based approach. Each version represents a distinct phase in the system’s evolution, with incremental improvements to functionality, usability, and security.

Version tags were used to capture stable states of the system throughout development, allowing for traceability and validation of progress over time.

---

## Version Milestones

### v0.1 – working-local-vault

- Initial implementation of local-first document storage
- Basic HTTP server established
- PDF ingestion and file storage to local directory
- Proof of concept for core architecture

---

### v0.2 – preview-ready

- Project documentation improvements (README and structure)
- Codebase cleanup and organization
- Introduction of HTML templates for UI rendering
- Initial user interface framework established

---

### v0.3 – search-working

- Implementation of keyword-based search functionality
- Introduction of SHA-256 hashing for duplicate detection
- Preservation of original filenames during ingestion
- Bug fixes related to duplicate file handling
- Addition of metadata-driven retrieval capabilities

---

### v0.4 – sensitivity-aware

- Introduction of sensitivity classification system
- Support for document tagging based on risk level (low, moderate, high, critical)
- Sensitivity-based filtering in search results
- UI warning system for sensitive document access
- Foundation for future policy-based controls

---

### v0.5 – template-refactor

- Refactoring of HTML template structure for improved maintainability
- Separation of presentation logic from core functionality
- Improved rendering consistency across pages
- Code cleanup and simplification of template utilities

---

### v0.6 – ui-polish

- User interface enhancements using Bootstrap styling
- Dashboard improvements, including document statistics display
- Improved user feedback (success messages, alerts)
- Enhanced usability and navigation across application pages

---

### v0.7 – secure-access

- Implementation of password-based authentication system
- Secure password hashing with salt (PBKDF2)
- Session management using secure tokens
- Session expiration enforcement (30-minute timeout)
- Login and logout functionality integrated into UI
- Route protection for sensitive endpoints
- Introduction of audit logging (`auth.log`) for authentication and access events

---

## Development Progression Summary

The system evolved through the following stages:

1. Core functionality (ingestion and storage)
2. Retrieval and search capabilities
3. Metadata enrichment and sensitivity awareness
4. User interface improvements
5. Security implementation and access control

This progression reflects a shift from a basic document manager to a more structured and security-aware system.

---

## Versioning Strategy

Version numbers were assigned to represent meaningful functional milestones rather than minor incremental changes. Each tagged version corresponds to a stable and testable state of the application.

The absence of patch-level versioning (e.g., v0.7.1) reflects the academic scope of the project, where emphasis was placed on major feature delivery rather than continuous deployment.

---

## Final Notes

The version history demonstrates a consistent and deliberate development process, with each iteration building upon previous functionality while introducing new capabilities.

This structured approach supports traceability, reproducibility, and evaluation of system progress throughout the lifecycle of the project.
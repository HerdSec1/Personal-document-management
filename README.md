# Local-First Personal Document Management System (Prototype)

## Project Overview

This repository contains a **design-phase prototype** for a local-first personal document management system intended to explore secure, offline-first handling of sensitive personal documents such as health records, financial statements, legal paperwork, and identification files.

The system is being developed as part of an academic semester project. At this stage, the repository primarily reflects **project structure, design intent, and planned architecture**, rather than a completed or functional application.

All data is intended to remain local to the user’s machine. No cloud services, telemetry, or external data sharing are planned.

---

## Problem Statement

Many individuals manage sensitive personal documents using ad-hoc folder structures or generic cloud storage tools. These approaches often lack consistent organization, meaningful metadata, and basic integrity awareness, while also introducing unnecessary privacy risks.

This project explores how a **simple, local-first system** can improve document organization and retrieval while applying foundational cybersecurity concepts in a realistic, constrained scope.

---

## Project Status

**Current Phase:**  
Early design and repository scaffolding (academic prototype)

**Implemented**
- Repository structure
- Documentation and design notes

**Planned (Not Yet Implemented)**
- Local ingestion of PDF documents
- Managed local storage for ingested files
- Metadata storage using SQLite
- Basic metadata-based listing and search
- Simple CLI-based interaction
- Integrity indicators (e.g., hashes, timestamps)

**Out of Scope**
- Multi-user support
- Cloud synchronization or backups
- Advanced access control models
- Compliance certifications or audits
- Production-grade security guarantees

No functional features are currently implemented. All technical capabilities described in this repository represent **design goals**, not completed functionality.

---

## Intended Functionality (Design Goals)

When implemented, the system is intended to:

- Accept local PDF files for ingestion
- Copy documents into managed local storage using safe filenames
- Track document metadata (e.g., filename, category, tags) in SQLite
- Provide basic listing and search over stored metadata
- Offer a simple command-line interface for interaction

These features are aspirational and subject to change as development progresses.

---

## Design Principles

**Local-First Architecture**  
All documents and metadata are intended to be stored and processed locally, without reliance on external services.

**Data Minimization**  
Only information necessary for organization and retrieval will be collected.

**Transparency and User Control**  
Users should be able to inspect where data is stored and how it is processed.

---

## Planned System Architecture (High-Level)

The proposed system architecture includes the following conceptual components:

- **Ingestion Module**  
  Responsible for accepting PDF files and registering them with the system.

- **Metadata Management**  
  Stores structured metadata in a local SQLite database.

- **Search & Retrieval**  
  Provides basic metadata-based queries.

- **Storage Layer**  
  Maintains documents and metadata on local disk in an inspectable format.

This architecture is intentionally minimal to remain feasible within a single academic term.

---

## Security Considerations (Design-Level)

**Intended Protections**
- Reduced exposure by avoiding cloud services
- Improved document organization
- Basic integrity awareness through hashing (planned)

**Explicit Non-Goals**
- Protection against a compromised host OS
- Defense against malware or malicious local users
- Physical security of the device
- Advanced or adversarial threat models

Security controls are limited by scope and are discussed at a conceptual level only.

---

## Installation & Setup

No runnable application is currently available.

This repository is in an early design phase. Installation, setup, and execution instructions will be added once functional components are implemented.

---

## Limitations

- No executable functionality at this stage
- Design-focused documentation only
- No validated security controls
- No production readiness

**Disclaimer**  
This project is an academic prototype and should not be used to manage real sensitive data.

---

## Future Work

Potential future work includes (not guaranteed):

- Implementation of ingestion and metadata storage
- CLI-based interaction
- SQLite schema refinement
- Basic integrity indicators
- Improved documentation and testing

---

## Repository Structure

- [`src/`](/src/) – Planned application logic (currently skeletal)
- [`data/`](/data/) – Intended location for local document storage
- [`docs/`](/docs/) – Design notes, architecture, and progress documentation
- [`LICENSE`](/LICENSE) – License information
- [`README.md`](/README.md) – Project overview and design intent

---

## Academic Context

This project is part of a university senior capstone course. It is intended strictly for educational and demonstrative purposes, with an emphasis on thoughtful system design, scope management, and the application of cybersecurity principles in a realistic setting.

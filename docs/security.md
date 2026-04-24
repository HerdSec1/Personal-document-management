# Security Implementation

## Overview

PerDocMan implements a lightweight authentication and session management system designed for a local-first application. While not intended as a production-grade security system, it introduces foundational security controls including password hashing, session validation, and audit logging.

The system prioritizes minimizing external exposure while maintaining transparency and simplicity appropriate for a prototype environment.

---

## Authentication Design

Authentication is implemented using a password-based system.

- Passwords are hashed using PBKDF2 with SHA-256
- A unique salt is generated for each password
- Hash comparison is performed using constant-time comparison (`hmac.compare_digest`) to mitigate timing attacks

This approach ensures that plaintext passwords are never stored or directly compared during authentication.

---

## Session Management

Upon successful login:

- A secure session token is generated using a cryptographically strong random function (`secrets.token_urlsafe`)
- The token is stored in server memory alongside a timestamp
- The token is issued to the client via an HTTP-only cookie

Session validation occurs on every request to protected routes.

### Session Expiration

- Sessions expire after 30 minutes of inactivity
- Expired sessions are automatically invalidated and removed from memory
- Users attempting to access protected resources after expiration are redirected to the login page

This mechanism reduces the risk of unauthorized reuse of stale session tokens.

---

## Route Protection

The application enforces authentication checks on all sensitive endpoints.

Protected routes include:

- `/`
- `/documents`
- `/search`
- `/doc`
- `/doc_raw`
- `/ingest`
- `/reset`

If a request is made to a protected route without a valid session, the user is redirected to the login interface.

---

## Audit Logging

Authentication and access events are recorded in a local audit log file (`auth.log`).

Events logged include:

- Successful login attempts
- Failed login attempts
- Logout events
- Document access events
- Sensitive document warning events

Each log entry contains:

- UTC timestamp
- Event type
- Client IP address
- Optional contextual details (e.g., document ID, filename)

This provides traceability of user activity without exposing document contents.

---

## Sensitive Document Handling

Documents classified as **high** or **critical** sensitivity trigger an additional warning step before being opened.

- Users are presented with a warning page
- Explicit confirmation is required before accessing the document
- Access attempts are logged as audit events

This mechanism increases user awareness of sensitive content and reduces accidental exposure.

---

## Security Controls Summary

The following controls are implemented in the current version:

- Local-only server binding (`127.0.0.1`)
- Password hashing with PBKDF2 and salt
- Secure session token generation
- Session expiration enforcement
- HTTP-only session cookies
- Audit logging of authentication and access events
- Sensitivity-based access warnings
- Parameterized SQL queries for database access
- HTML escaping to mitigate injection risks

---

## Security Limitations

As a prototype system, the following limitations are acknowledged:

- No encryption at rest for stored documents
- No multi-user or role-based access control
- Sessions are stored in memory and are not persistent across restarts
- No HTTPS support (local HTTP only)
- Assumes a trusted local machine environment
- Audit logs are not tamper-resistant

These limitations are intentionally accepted within the scope of a local-first academic prototype.

---

## Future Enhancements

Potential improvements to the security model include:

- Encryption at rest for stored documents
- Role-based access control (RBAC)
- Persistent and secure session storage
- Stronger password policies and configuration management
- Optional TLS support for secure local network access
- Enhanced audit logging with integrity protection

---

## Security Perspective

This implementation reflects foundational cybersecurity principles:

- **Confidentiality** through local-only data handling
- **Integrity** through hashing and controlled ingestion workflows
- **Availability** through lightweight, self-contained system design

Rather than relying on external systems, PerDocMan demonstrates how core security concepts can be applied within a constrained, local-first architecture.
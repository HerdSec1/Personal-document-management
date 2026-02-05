# Security Model

## Design Philosophy

PerDocMan.exe is designed to reduce unnecessary exposure of sensitive personal documents by operating entirely on a local machine. The system prioritizes transparency, inspectability, and reduced attack surface over advanced cryptographic controls.

This is a prototype system, not a hardened security product.

---

## Threat Assumptions

### In-Scope Threats
- Accidental data exposure through cloud services
- Loss of document context due to poor organization
- Undetected modification of stored files

### Out-of-Scope Threats
- Compromised host operating system
- Malware or malicious local users
- Physical access to the device
- Advanced targeted attacks
- Key management and encryption-at-rest

---

## Security Controls

### Local-Only Operation
- HTTP server binds to `127.0.0.1`
- No network interfaces are exposed
- No background services persist after application exit

### File System Security
- Document vault relies on Windows file system permissions
- Files are stored under the user’s profile directory
- The application closes all file handles on shutdown

### Integrity Awareness
- SHA-256 hash computed and stored at ingestion
- Hash comparison can be used to detect file modification
- Integrity indicators are informational, not enforcement mechanisms

### Audit and Session Logging
- Session start and end times recorded
- User and host information logged
- Logging focuses on events, not document contents

---

## Security Limitations

- The system cannot prevent access by other processes running under the same user account
- No encryption is applied to stored documents in the current scope
- Audit logs are informational and do not provide tamper resistance

---

## Security Transparency

All security measures and limitations are documented to avoid overstating protection capabilities.

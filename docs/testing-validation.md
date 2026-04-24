# Testing and Validation

## Overview

PerDocMan was tested through a series of manual validation scenarios designed to verify functional correctness, data integrity, and security-related behaviors. As a prototype system, testing focuses on validating core workflows rather than implementing a full automated test suite.

Testing was performed incrementally alongside development to ensure that each major feature operated as expected before progressing to the next stage.

---

## Testing Approach

The system was validated using:

- Manual functional testing of user workflows
- Targeted scenario-based validation
- Inspection of database state (SQLite)
- Review of audit logs (`auth.log`)
- Iterative testing during feature development

This approach ensured that each system component behaved correctly within the local-first design constraints.

---

## Core Functional Tests

### Application Startup

**Test:**
- Launch application using the launcher script

**Expected Result:**
- Local HTTP server starts successfully
- Browser opens to the application dashboard
- Session record is created in the database

---

### Document Ingestion

**Test:**
- Upload a valid PDF file through the dashboard

**Expected Result:**
- File is copied to the managed storage directory
- Metadata is inserted into the SQLite database
- Document appears in the dashboard and document list
- Success message is displayed to the user

---

### Duplicate Document Detection

**Test:**
- Attempt to upload the same PDF file multiple times

**Expected Result:**
- System detects duplicate using SHA-256 hash
- Duplicate file is rejected
- No additional file is stored
- No duplicate database record is created

---

### Search Functionality

**Test:**
- Perform keyword searches using document metadata and content preview

**Expected Result:**
- Relevant documents are returned
- Results reflect query filters (keywords, sensitivity)
- No system errors occur during query execution

---

### Sensitivity Filtering

**Test:**
- Apply sensitivity filters during search

**Expected Result:**
- Only documents meeting the selected sensitivity level are returned
- Lower-tier documents are excluded when higher sensitivity filters are applied

---

### Sensitive Document Warning

**Test:**
- Attempt to open a document marked as high or critical sensitivity

**Expected Result:**
- Warning page is displayed before document access
- User must explicitly confirm to proceed
- Event is recorded in the audit log

---

## Security Validation Tests

### Authentication – Successful Login

**Test:**
- Enter correct password on login page

**Expected Result:**
- User is authenticated
- Session token is issued
- User is redirected to the dashboard
- Event is logged as SUCCESSFUL_LOGIN

---

### Authentication – Failed Login

**Test:**
- Enter incorrect password

**Expected Result:**
- Login is rejected
- User remains on login page
- Error message is displayed
- Event is logged as FAILED_LOGIN

---

### Session Persistence

**Test:**
- Navigate between protected routes after login

**Expected Result:**
- User remains authenticated
- Session is maintained across requests

---

### Session Expiration

**Test:**
- Allow session to expire (tested using shortened timeout during development)

**Expected Result:**
- Session is invalidated after timeout period
- User is redirected to login page when accessing protected routes

---

### Logout Behavior

**Test:**
- Click logout from dashboard or navigation

**Expected Result:**
- Session token is removed
- Cookie is cleared
- User is redirected to login page
- Event is logged as LOGGED_OUT

---

## Data Integrity Validation

### File-System Consistency

**Test:**
- Access document records with valid and invalid file paths

**Expected Result:**
- Valid documents are served correctly
- Missing files trigger error response
- System does not attempt unsafe recovery

---

### Database Reset

**Test:**
- Trigger database reset from dashboard

**Expected Result:**
- All document records are removed
- Stored PDF files are deleted
- Database schema remains intact
- System remains operational after reset

---

## Logging Validation

**Test:**
- Perform authentication and document access actions

**Expected Result:**
- Events are written to `auth.log`
- Entries include timestamp, event type, and client IP
- Log file grows incrementally with system usage

---

## Limitations of Testing

- No automated unit or integration test suite implemented
- Testing performed in a controlled local environment only
- No performance or stress testing conducted
- No multi-user concurrency testing performed

---

## Validation Summary

Testing confirms that:

- Core system workflows operate as expected
- Authentication and session controls function correctly
- Data integrity mechanisms prevent duplication and inconsistency
- Logging provides traceability of key system events

The system demonstrates reliable behavior within the defined scope of a local-first prototype.
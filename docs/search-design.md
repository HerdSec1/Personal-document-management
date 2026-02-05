# Search and Indexing Design

## Definition of Indexing

In this project, *indexing* refers to the creation of a structured SQLite metadata database and associated database indexes that support efficient retrieval of documents without manual folder traversal.

Indexing does **not** refer to semantic embeddings, LLM-based search, or cloud-backed indexing services.

---

## Metadata Schema

Each ingested document is represented by a row in the `documents` table with fields including:

- Original filename
- Managed storage path
- SHA-256 hash
- Category
- Tags (comma-separated, prototype format)
- Document date
- Ingestion timestamp

---

## Database Indexes

To support efficient queries, SQLite indexes are created on frequently queried fields, such as:

- Category
- Document date
- Ingestion timestamp

These indexes allow retrieval without scanning the entire dataset.

---

## Search Mechanisms

### Tier 1: Structured Metadata Search (Guaranteed Scope)

- Exact match on category
- Partial match on tags
- Date range filtering
- Sorting by document date or ingestion time

All searches are executed as parameterized SQL queries.

---

### Tier 2: Human-Readable Query Parsing (Prototype)

To improve usability, the system supports simple, rule-based parsing of natural query phrases. These phrases are translated into structured SQL filters.

#### Supported Query Patterns (Prototype)
- `<keywords>`
- `<keywords> since <year>`
- `<keywords> before <year>`
- `<keywords> between <year> and <year>`

#### Example
User input:
`Lab work since 2020`

Interpreted as:
- Tags contain "lab" (or category mapped to health)
- Document date ≥ 2012-01-01

Compiled SQL:
```sql
SELECT * FROM documents
WHERE tags LIKE '%lab%'
AND doc_date >= '2012-01-01';

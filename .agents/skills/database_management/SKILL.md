---
name: "database_management"
description: "Guidelines and standards for database schema design, migrations, security, and query optimization."
tier: 2
---

# Database Management Standards

This skill defines the mandatory standards and operational guidelines for database schema design, migration management, query optimization, and data security.

## Database Design, Naming, and Modularity

- **Naming Conventions**: Enforce consistent use of underscores (`_`) for database field names, table names, indexes, and schema directories. Do not use hyphens or dashes as separators.
- **Data Layout and Presentation**: Use standardized Markdown tables to document database configuration matrices, schema relationships, and mapping definitions.
- **Modular and Clean SQL**: Write structured, readable, and self-documenting SQL queries. Follow style guides for SQL formatting, ensuring low coupling and clear logical partitioning where applicable.

## Schema Migration Management

- **Automated Migrations**: Enforce version-controlled, automated migration tools (e.g., Liquibase, Flyway, Alembic, or active record migrations) to manage all schema updates. Ad-hoc or manual SQL schema changes are strictly prohibited in any environment.
- **Idempotency**: All migration scripts must be idempotent and support clean rollback procedures. Verify that migrations can be applied and reverted successfully in a staging environment prior to production deployment.

## Data Security and Privacy

- **Data Masking**: Automatically mask or anonymize all Personally Identifiable Information (PII) and Protected Health Information (PHI) when replicating production data to lower environments (development, testing, staging).
- **Access Control and Secrets**: Restrict database access using the principle of least privilege. Database credentials must be retrieved dynamically from secure secret managers (e.g., AWS Secrets Manager, HashiCorp Vault) and never hardcoded or committed to version control.
- **Secure Connections**: Enforce secure-by-default options, disabling insecure connection protocols and requiring SSL/TLS for all database transport.

## Input Validation and Defensive Error Handling

- **Input Validation**: Never trust external or internal input parameters. Enforce strict input validation, type safety, and parameterized queries (prepared statements) to prevent SQL injection and data corruption.
- **Defensive Error Handling**: Catch, handle, and log database exceptions gracefully. Do not expose database schemas, driver details, or internal stack traces to end users.
- **Structured Failure Reporting**: Emit structured log payloads (e.g., JSON format) for all database connection failures, transaction errors, or slow queries, detailing the error vector, timestamp, and relevant query context.

## Performance Optimization and Resiliency

- **Query Profiling**: Utilize `EXPLAIN` and `EXPLAIN ANALYZE` commands to profile query execution plans before deploying new queries or modifications. Ensure index utilization is optimized.
- **Lock Contention**: Design transaction blocks to be as short as possible to minimize lock contention and prevent deadlocks. Avoid performing external API calls or blocking operations inside database transactions.
- **Indexing**: Maintain appropriate indexing strategies for frequently queried fields, while avoiding over-indexing which degrades write performance.
- **Execution Resiliency**: Design database connections with explicit timeouts, connection pool sizing, non-blocking execution options, and liveness checks to ensure system resilience.

## Reliability and Disaster Recovery

- **Backup Verification**: Establish automated, scheduled database backup routines (including full, differential, and transaction log backups) with encryption at rest.
- **Restoration Drills**: Conduct periodic disaster recovery simulations and database restoration drills to ensure recovery time objectives (RTO) and recovery point objectives (RPO) can be consistently met.

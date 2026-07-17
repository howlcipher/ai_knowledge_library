---
name: "database_management"
description: "Guidelines and standards for database schema design, migrations, security, and query optimization."
---

# Database Management Standards

This skill defines the mandatory standards and operational guidelines for database schema design, migration management, query optimization, and data security.

## Schema Migration Management

- **Automated Migrations**: Enforce version-controlled, automated migration tools (e.g., Liquibase, Flyway, Alembic, or active record migrations) to manage all schema updates. Ad-hoc or manual SQL schema changes are strictly prohibited in any environment.
- **Idempotency**: All migration scripts must be idempotent and support clean rollback procedures. Verify that migrations can be applied and reverted successfully in a staging environment prior to production deployment.

## Data Security and Privacy

- **Data Masking**: Automatically mask or anonymize all Personally Identifiable Information (PII) and Protected Health Information (PHI) when replicating production data to lower environments (development, testing, staging).
- **Access Control**: Restrict database access using the principle of least privilege. Database credentials must be retrieved dynamically from secure secret managers (e.g., AWS Secrets Manager, HashiCorp Vault) and never hardcoded or committed to version control.

## Performance Optimization

- **Query Profiling**: Utilize `EXPLAIN` and `EXPLAIN ANALYZE` commands to profile query execution plans before deploying new queries or modifications. Ensure index utilization is optimized.
- **Lock Contention**: Design transaction blocks to be as short as possible to minimize lock contention and prevent deadlocks. Avoid performing external API calls or blocking operations inside database transactions.
- **Indexing**: Maintain appropriate indexing strategies for frequently queried fields, while avoiding over-indexing which degrades write performance.

## Reliability and Disaster Recovery

- **Backup Verification**: Establish automated, scheduled database backup routines (including full, differential, and transaction log backups) with encryption at rest.
- **Restoration Drills**: Conduct periodic disaster recovery simulations and database restoration drills to ensure recovery time objectives (RTO) and recovery point objectives (RPO) can be consistently met.

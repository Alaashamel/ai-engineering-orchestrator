#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_URL="${DATABASE_URL:-postgresql://app:app_password@localhost:5432/ai_software_company}"
pg_dump "$DB_URL" > "backup_${TIMESTAMP}.sql"
echo "Backup saved to backup_${TIMESTAMP}.sql"

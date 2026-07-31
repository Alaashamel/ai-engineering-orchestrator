#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi
DB_URL="${DATABASE_URL:-postgresql://app:app_password@localhost:5432/ai_software_company}"
pg_restore -d "$DB_URL" "$1" || psql "$DB_URL" < "$1"
echo "Restored from $1"

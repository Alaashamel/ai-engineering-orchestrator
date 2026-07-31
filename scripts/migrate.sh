#!/bin/bash
set -e
ALEMBIC_CMD="cd apps/api && alembic"
echo "Running database migrations..."
$ALEMBIC_CMD upgrade head
echo "Current revision:"
$ALEMBIC_CMD current

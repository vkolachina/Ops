#!/bin/bash
# main_migration.sh

echo "Starting migration process"

# Perform audit
./audit_cicd.sh

# Perform dry runs
./dry_run_migration.sh

# Analyze dry runs
python analyze_dry_runs.py

# Prompt user to continue
read -p "Do you want to proceed with the migration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Perform actual migration
./perform_migration.sh

echo "Migration completed"
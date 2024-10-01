#!/bin/bash
# dry_run_migration.sh

ORG_NAME="your_organization_name"
OUTPUT_DIR="./dry_runs"

mkdir -p $OUTPUT_DIR

REPOS=$(gh repo list $ORG_NAME --json name --jq '.[].name')

for REPO in $REPOS; do
  echo "Performing dry run for $REPO"
  gh actions-importer dry-run [CI-PLATFORM] \
    --source-url [SOURCE_URL]/$REPO \
    --output-dir $OUTPUT_DIR/$REPO
done

echo "Dry runs completed. Results saved in $OUTPUT_DIR"
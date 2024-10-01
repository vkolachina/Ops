#!/bin/bash
# perform_migration.sh

ORG_NAME="your_organization_name"
OUTPUT_DIR="./migration_results"

mkdir -p $OUTPUT_DIR

REPOS=$(gh repo list $ORG_NAME --json name --jq '.[].name')

for REPO in $REPOS; do
  echo "Migrating $REPO"
  gh actions-importer migrate [CI-PLATFORM] \
    --source-url [SOURCE_URL]/$REPO \
    --target-url https://github.com/$ORG_NAME/$REPO \
    --output-dir $OUTPUT_DIR/$REPO \
    --custom-transformers custom_transformers.rb
done

echo "Migration completed. Results saved in $OUTPUT_DIR"
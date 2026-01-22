#!/bin/bash

# --- CONFIGURATION ---
PRIVATE_REPO_URL="https://github.com/elisaot/Master.git"
PUBLIC_REPO_URL="https://github.com/elisaot/Master-Project.git"
SYNC_BRANCH="public-sync"       # Branch for public repo
PRIVATE_DIRS=("data_collection/scrape-NRK/nrk_tegnspraaknytt" "data_collection/scrape-SL/videos" "data_collection/scrape-SL/unexpected_vid" "data_collection/preprocess_news/clips" "data_collection/tables" "data_collection/signpuddle/sgn69.db" "experiment_single_sign/results")  # Folders/files to remove
WORK_DIR="$HOME/tmp/private_repo_sync"

# --- 1. Prepare working directory ---
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR" || exit 1

# --- 2. Clone private repo ---
git clone "$PRIVATE_REPO_URL" repo
cd repo || exit 1

# --- 3. Create orphan branch for public sync ---
git checkout --orphan "$SYNC_BRANCH"

# --- 4. Remove private files/folders ---
for dir in "${PRIVATE_DIRS[@]}"; do
    rm -rf "$dir"
done

# Optional: scrub sensitive data inside files (example)
if [ -f config.json ]; then
    jq 'del(.api_key, .secret)' config.json > config_clean.json
    mv config_clean.json config.json
fi

# --- 5. Commit cleaned repo ---
git add -A
git commit -m "Sync cleaned version to public repo"

# --- 6. Add public repo and push ---
git remote add public "$PUBLIC_REPO_URL"
git push --force public "$SYNC_BRANCH":main

echo "Public repo updated successfully!"
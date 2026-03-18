#!/bin/sh
set -e

# 1. Load InsuranceQA-v2 (1000 docs to limit embedding cost)
echo "Loading Insurance RAG data (1000 docs)..."
python /app/scripts/load_insurance_qa.py --max-rows 1000 --output-dir /app/app/data/insurance || true

# 2. Pre-build FAISS index (requires OPENAI_API_KEY)
echo "Pre-building FAISS index..."
python /app/scripts/prebuild_faiss.py || true

# 3. Start the application
exec "$@"

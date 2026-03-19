#!/usr/bin/env python3
"""
Load InsuranceQA-v2 from Hugging Face and convert to markdown for RAG.

Dataset: https://huggingface.co/datasets/deccan-ai/insuranceQA-v2
- input: question
- output: answer

Usage:
    python scripts/load_insurance_qa.py [--max-rows 2000] [--output-dir app/data/insurance]
"""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Load InsuranceQA-v2 to markdown for RAG")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=1000,
        help="Max Q&A pairs to include (default: 1000). Use 0 for all ~28k.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "app" / "data" / "insurance",
        help="Output directory for markdown files",
    )
    parser.add_argument(
        "--split",
        choices=["train", "validation", "test", "all"],
        default="train",
        help="Dataset split to use (default: train)",
    )
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError:
        print("Install datasets: pip install datasets")
        return 1

    print("Loading deccan-ai/insuranceQA-v2 from Hugging Face...")
    if args.split == "all":
        ds = load_dataset("deccan-ai/insuranceQA-v2", split="train+validation+test")
    else:
        ds = load_dataset("deccan-ai/insuranceQA-v2", split=args.split)

    max_rows = args.max_rows if args.max_rows > 0 else len(ds)
    rows = min(max_rows, len(ds))
    ds = ds.select(range(rows))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / "insurance_qa.md"

    print(f"Converting {len(ds)} Q&A pairs to markdown...")
    blocks = []
    for i, row in enumerate(ds):
        q = row.get("input", "").strip()
        a = row.get("output", "").strip()
        if not q or not a:
            continue
        blocks.append(f"## Q: {q}\n\n{a}")

    content = "\n\n---\n\n".join(blocks)
    output_path.write_text(content, encoding="utf-8")
    print(f"Saved to {output_path} ({len(content):,} chars, {len(blocks)} Q&A pairs)")

    print("\nTo reindex Chroma (clear cached embeddings):")
    chroma_path = Path(__file__).parent.parent / "app" / "data" / "chroma_insurance"
    print(f"  rm -rf {chroma_path}")
    print("Then restart the app — Chroma will rebuild on first Insurance query.")

    return 0


if __name__ == "__main__":
    exit(main())

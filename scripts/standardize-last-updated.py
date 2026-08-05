#!/usr/bin/env python3
"""
Script to standardize "Last Updated" fields across all documentation files.
Updates all Last Updated dates to the current date.
"""

import re
from pathlib import Path
from datetime import date

def standardize_last_updated(docs_dir="docs", current_date=None):
    """
    Standardize Last Updated fields in all markdown files.
    """
    if current_date is None:
        current_date = date.today().isoformat()
    
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"Error: {docs_dir} directory not found")
        return
    
    # Find all markdown files
    md_files = list(docs_path.rglob("*.md"))
    
    updated_count = 0
    skipped_count = 0
    
    for md_file in md_files:
        content = md_file.read_text()
        
        # Check if file has Last Updated field
        if "Last Updated" not in content:
            print(f"Skipping {md_file}: No Last Updated field found")
            skipped_count += 1
            continue
        
        # Update Last Updated date
        # Pattern: Last Updated: YYYY-MM-DD
        pattern = r"Last Updated:.*\d{4}-\d{2}-\d{2}"
        replacement = f"Last Updated: {current_date}"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            md_file.write_text(new_content)
            print(f"✅ Updated {md_file}")
            updated_count += 1
        else:
            print(f"⏭️  Skipped {md_file}: Already up to date")
            skipped_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Updated: {updated_count} files")
    print(f"   Skipped: {skipped_count} files")
    print(f"   Total: {len(md_files)} files")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Standardize Last Updated fields in documentation")
    parser.add_argument("--date", help="Date to set (YYYY-MM-DD format, default: today)")
    parser.add_argument("--dir", default="docs", help="Documentation directory (default: docs)")
    
    args = parser.parse_args()
    
    standardize_last_updated(args.dir, args.date)

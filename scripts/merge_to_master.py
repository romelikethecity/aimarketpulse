#!/usr/bin/env python3
"""
Merge weekly enriched data into master database.
This ensures the master_jobs_database.csv is up to date for the website.
"""

import pandas as pd
import os
import glob
from datetime import datetime

DATA_DIR = "data"

print("="*70)
print("  AI MARKET PULSE - MERGE TO MASTER DATABASE")
print("="*70)

# Find most recent enriched file
enriched_files = glob.glob(f"{DATA_DIR}/ai_jobs_*.csv")
if not enriched_files:
    print("\n No enriched CSV files found")
    print("   Run enrich_jobs.py first")
    exit(0)

latest_enriched = max(enriched_files, key=os.path.getctime)
print(f"\n Latest enriched file: {latest_enriched}")

# Load new data
new_df = pd.read_csv(latest_enriched)
print(f" New records: {len(new_df)}")

# Add import metadata
new_df['import_date'] = datetime.now().strftime('%Y-%m-%d')
new_df['import_week'] = datetime.now().strftime('%Y-W%W')

# Load or create master database
master_file = f"{DATA_DIR}/master_jobs_database.csv"

if os.path.exists(master_file):
    master_df = pd.read_csv(master_file)
    print(f" Existing master database: {len(master_df)} records")

    # Deduplicate based on job_url or source_url
    url_col = 'job_url_direct' if 'job_url_direct' in new_df.columns else 'source_url'

    if url_col in new_df.columns and url_col in master_df.columns:
        existing_urls = set(master_df[url_col].dropna().unique())
        new_records = new_df[~new_df[url_col].isin(existing_urls)]
        print(f" New unique records: {len(new_records)}")

        if len(new_records) > 0:
            combined_df = pd.concat([master_df, new_records], ignore_index=True)
        else:
            combined_df = master_df
            print("   No new records to add")
    else:
        # No URL column, just append
        combined_df = pd.concat([master_df, new_df], ignore_index=True)
else:
    print(" Creating new master database")
    combined_df = new_df

# Save master database
combined_df.to_csv(master_file, index=False)
print(f"\n Master database saved: {len(combined_df)} total records")

# Update historical tracking file for trend charts
tracking_file = f"{DATA_DIR}/job_count_history.csv"
today = datetime.now().strftime('%Y-%m-%d')
job_count = len(new_df)

if os.path.exists(tracking_file):
    tracking_df = pd.read_csv(tracking_file)

    # Only add if this date isn't already in the file
    if today not in tracking_df['date'].values:
        new_row = pd.DataFrame([{'date': today, 'job_count': job_count}])
        tracking_df = pd.concat([tracking_df, new_row], ignore_index=True)
        tracking_df.to_csv(tracking_file, index=False)
        print(f" Updated trend tracking: {today} -> {job_count} jobs")
    else:
        print(f" Trend tracking already has entry for {today}")
else:
    # Create new tracking file
    tracking_df = pd.DataFrame([{'date': today, 'job_count': job_count}])
    tracking_df.to_csv(tracking_file, index=False)
    print(f" Created trend tracking: {today} -> {job_count} jobs")

# Print stats
print(f"\n{'='*70}")
print(" MERGE COMPLETE")
print(f"{'='*70}")
print(f" Master database: {len(combined_df)} total jobs")
print(f" Latest import: {len(new_df)} jobs")

# Category breakdown
if 'job_category' in combined_df.columns:
    print("\n Top categories in master database:")
    cats = combined_df['job_category'].value_counts().head(5)
    for cat, count in cats.items():
        print(f"   {cat}: {count}")

print("="*70)

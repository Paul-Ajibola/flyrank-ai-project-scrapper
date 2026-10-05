import os
import json
import csv

OUTPUT_DIR = "output"

def export_to_json(records, filename="books.json"):
    """Exports validated records to a structured JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    # Convert Pydantic models to dictionaries if they aren't already
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in records]
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Successfully exported {len(data)} records to JSON: {file_path}")

def export_to_csv(records, filename="books.csv"):
    """Exports validated records to a structured CSV file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in records]
    if not data:
        print("No records available to export to CSV.")
        return

    # Extract field headers from the first record
    fieldnames = list(data[0].keys())
    
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Successfully exported {len(data)} records to CSV: {file_path}")
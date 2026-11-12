import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db import get_connection

def cleanup_residents():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Identify records for Tanishq and Abhinav
    cursor.execute(
        """
        SELECT resident_id, full_name, flat_number, image_path
        FROM residents
        WHERE LOWER(full_name) LIKE '%tanishq%' OR LOWER(full_name) LIKE '%abhinav%'
        """
    )
    keep_records = cursor.fetchall()
    keep_ids = [r["resident_id"] for r in keep_records]

    print(f"Preserving {len(keep_records)} resident(s):")
    for r in keep_records:
        print(f"  • ID #{r['resident_id']}: {r['full_name']} ({r['flat_number']}) -> {r['image_path']}")

    if not keep_ids:
        print("Warning: Neither Tanishq nor Abhinav was found. Aborting deletion.")
        conn.close()
        return

    placeholders = ",".join(["?"] * len(keep_ids))

    # 2. Find and delete image files of all other residents
    cursor.execute(
        f"SELECT resident_id, image_path FROM residents WHERE resident_id NOT IN ({placeholders})",
        keep_ids
    )
    to_delete = cursor.fetchall()
    deleted_images_count = 0
    for r in to_delete:
        img_path = Path(r["image_path"])
        if img_path.exists():
            try:
                os.remove(img_path)
                deleted_images_count += 1
            except Exception as e:
                print(f"Could not delete {img_path}: {e}")

    # 3. Clean up entry logs referencing deleted residents
    cursor.execute(
        f"DELETE FROM entry_logs WHERE resident_id IS NOT NULL AND resident_id NOT IN ({placeholders})",
        keep_ids
    )

    # 4. Delete all other residents
    cursor.execute(
        f"DELETE FROM residents WHERE resident_id NOT IN ({placeholders})",
        keep_ids
    )
    conn.commit()

    # 5. Verify remaining data
    cursor.execute("SELECT resident_id, full_name, flat_number, status, image_path FROM residents")
    remaining = cursor.fetchall()
    print("\nVerified Remaining Residents in Database:")
    for r in remaining:
        print(f"  • ID #{r['resident_id']}: {r['full_name']} | Flat: {r['flat_number']} | Status: {r['status']}")

    conn.close()
    print(f"\nCleanup complete: Deleted {len(to_delete)} other resident profiles and {deleted_images_count} image files.")

if __name__ == "__main__":
    cleanup_residents()


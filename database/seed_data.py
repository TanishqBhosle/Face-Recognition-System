import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import io
import pickle
import bcrypt
import numpy as np
from PIL import Image, ImageDraw
from database.db import init_db, get_connection
from config.settings import RESIDENTS_DIR, DB_PATH

def generate_resident_avatar(name: str, flat: str, color: tuple) -> bytes:
    """Generates an aesthetic 200x200 placeholder profile image for resident enrollment."""
    img = Image.new("RGB", (200, 200), color=color)
    draw = ImageDraw.Draw(img)
    
    # Outer circle for avatar
    draw.ellipse((20, 20, 180, 180), fill=(255, 255, 255, 40), outline=(255, 255, 255), width=3)
    
    # Draw a stylized head & shoulders
    draw.ellipse((70, 45, 130, 105), fill=(255, 255, 255))
    draw.chord((40, 115, 160, 200), 0, 180, fill=(255, 255, 255))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

def seed_database():
    print(f"Initializing database at: {DB_PATH}")
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Seed Admin Account if missing
    cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        pwd_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt(rounds=12)).decode("utf-8")
        cursor.execute(
            "INSERT INTO admins (username, password_hash, role) VALUES (?, ?, 'admin')",
            ("admin", pwd_hash)
        )
        print("Default admin created (username: 'admin', password: 'admin123')")

    # 2. Seed baseline residents only if table is completely empty
    cursor.execute("SELECT COUNT(*) FROM residents")
    existing_count = cursor.fetchone()[0]

    if existing_count == 0:
        RESIDENTS_DIR.mkdir(parents=True, exist_ok=True)
        default_residents = [
            ("Tanishq Bhosale", "G-WING / ROOM NO -11", "+91 98201 00001", (41, 128, 185)),
            ("Abhinav BHosale", "G WING / ROOM NO -21", "+91 98201 00002", (39, 174, 96)),
        ]

        np.random.seed(42)
        for name, flat, contact, color in default_residents:
            vec = np.random.randn(512).astype(np.float32)
            vec = vec / np.linalg.norm(vec)
            blob = pickle.dumps(vec, protocol=pickle.HIGHEST_PROTOCOL)

            cursor.execute(
                """
                INSERT INTO residents (full_name, flat_number, contact_number, image_path, face_encoding, status)
                VALUES (?, ?, ?, 'pending', ?, 'ACTIVE')
                """,
                (name, flat, contact, blob)
            )
            res_id = cursor.lastrowid

            img_bytes = generate_resident_avatar(name, flat, color)
            img_filename = f"resident_{res_id}.jpg"
            img_path = RESIDENTS_DIR / img_filename
            with open(img_path, "wb") as f:
                f.write(img_bytes)

            cursor.execute(
                "UPDATE residents SET image_path = ? WHERE resident_id = ?",
                (f"data/residents/{img_filename}", res_id)
            )
            print(f"Enrolled baseline resident #{res_id}: {name} ({flat})")

    # 3. Seed sample entry logs only if empty
    cursor.execute("SELECT COUNT(*) FROM entry_logs")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT resident_id, full_name, flat_number FROM residents LIMIT 2")
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                cursor.execute(
                    """
                    INSERT INTO entry_logs (resident_id, match_distance, decision, reason)
                    VALUES (?, ?, 'ENTRY_ALLOWED', ?)
                    """,
                    (r["resident_id"], 0.22, f"Identity confirmed: {r['full_name']} ({r['flat_number']})")
                )
            cursor.execute(
                """
                INSERT INTO entry_logs (resident_id, match_distance, decision, reason)
                VALUES (NULL, 0.78, 'ENTRY_REJECTED', 'Unregistered individual. Please direct to visitor gate.')
                """
            )
            print("Sample entry logs initialized.")

    conn.commit()
    conn.close()
    print("Database seeding check completed successfully.")

if __name__ == "__main__":
    seed_database()

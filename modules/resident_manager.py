import io
import pickle
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from PIL import Image

from database.db import get_connection, get_db_cursor
from config.settings import RESIDENTS_DIR

@dataclass
class Resident:
    resident_id: int
    full_name: str
    flat_number: str
    contact_number: Optional[str]
    image_path: str
    face_encoding: np.ndarray
    status: str
    created_at: str
    updated_at: str

class ResidentManager:
    """
    Manages resident profile persistence, photo storage, embedding serialization,
    and duplicate face detection.
    """
    def __init__(self):
        RESIDENTS_DIR.mkdir(parents=True, exist_ok=True)

    def register_resident(
        self,
        full_name: str,
        flat_number: str,
        contact_number: Optional[str],
        image_bytes: bytes,
        face_encoding: np.ndarray
    ) -> int:
        """
        Saves photo to disk, serializes embedding vector, inserts record into DB.
        Returns the new resident_id.
        """
        # Serialize the numpy embedding vector to bytes
        blob_encoding = pickle.dumps(face_encoding, protocol=pickle.HIGHEST_PROTOCOL)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO residents (full_name, flat_number, contact_number, image_path, face_encoding, status)
                VALUES (?, ?, ?, ?, ?, 'ACTIVE')
                """,
                (full_name.strip(), flat_number.strip().upper(), contact_number, "pending", blob_encoding)
            )
            resident_id = cursor.lastrowid

            # Save reference photo
            photo_filename = f"resident_{resident_id}.jpg"
            photo_path = RESIDENTS_DIR / photo_filename
            
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("RGB")
            image.save(photo_path, "JPEG", quality=92)

            # Update the stored image_path relative to project root
            relative_image_path = f"data/residents/{photo_filename}"
            cursor.execute(
                "UPDATE residents SET image_path = ? WHERE resident_id = ?",
                (relative_image_path, resident_id)
            )
            conn.commit()
            return resident_id
        finally:
            conn.close()

    def get_all_active_residents(self) -> List[Resident]:
        """
        Returns all residents with status == 'ACTIVE', deserializing their face embeddings.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT resident_id, full_name, flat_number, contact_number,
                       image_path, face_encoding, status, created_at, updated_at
                FROM residents
                WHERE status = 'ACTIVE'
                ORDER BY full_name ASC
                """
            )
            rows = cursor.fetchall()
            residents = []
            for row in rows:
                encoding = pickle.loads(row["face_encoding"])
                residents.append(Resident(
                    resident_id=row["resident_id"],
                    full_name=row["full_name"],
                    flat_number=row["flat_number"],
                    contact_number=row["contact_number"],
                    image_path=row["image_path"],
                    face_encoding=encoding,
                    status=row["status"],
                    created_at=str(row["created_at"]),
                    updated_at=str(row["updated_at"])
                ))
            return residents
        finally:
            conn.close()

    def get_all_residents(self) -> List[Dict[str, Any]]:
        """
        Returns all residents (both ACTIVE and INACTIVE) without deserializing full embeddings for grid view.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT resident_id, full_name, flat_number, contact_number,
                       image_path, status, created_at, updated_at
                FROM residents
                ORDER BY resident_id DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_resident_by_id(self, resident_id: int) -> Optional[Resident]:
        """Fetches single resident by ID."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM residents WHERE resident_id = ?", (resident_id,))
            row = cursor.fetchone()
            if not row:
                return None
            encoding = pickle.loads(row["face_encoding"])
            return Resident(
                resident_id=row["resident_id"],
                full_name=row["full_name"],
                flat_number=row["flat_number"],
                contact_number=row["contact_number"],
                image_path=row["image_path"],
                face_encoding=encoding,
                status=row["status"],
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"])
            )
        finally:
            conn.close()

    def update_resident(
        self,
        resident_id: int,
        full_name: str,
        flat_number: str,
        contact_number: Optional[str] = None
    ) -> bool:
        """Updates resident metadata."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE residents
                SET full_name = ?, flat_number = ?, contact_number = ?
                WHERE resident_id = ?
                """,
                (full_name.strip(), flat_number.strip().upper(), contact_number, resident_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def set_status(self, resident_id: int, status: str) -> bool:
        """Toggles status between 'ACTIVE' and 'INACTIVE'."""
        if status not in ("ACTIVE", "INACTIVE"):
            raise ValueError(f"Invalid status: {status}")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE residents SET status = ? WHERE resident_id = ?",
                (status, resident_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_photo_and_embedding(
        self,
        resident_id: int,
        image_bytes: bytes,
        new_face_encoding: np.ndarray
    ) -> bool:
        """Updates the resident's reference image on disk and updates the embedding blob in DB."""
        photo_filename = f"resident_{resident_id}.jpg"
        photo_path = RESIDENTS_DIR / photo_filename
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image.save(photo_path, "JPEG", quality=92)

        blob_encoding = pickle.dumps(new_face_encoding, protocol=pickle.HIGHEST_PROTOCOL)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE residents SET face_encoding = ? WHERE resident_id = ?",
                (blob_encoding, resident_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def check_duplicate(self, candidate_encoding: np.ndarray, threshold: float = 0.35) -> Optional[Resident]:
        """
        Compares candidate encoding against all active residents.
        Returns the existing matching Resident if cosine distance <= threshold.
        """
        active_residents = self.get_all_active_residents()
        for res in active_residents:
            u = candidate_encoding.flatten()
            v = res.face_encoding.flatten()
            dot = np.dot(u, v)
            norm_u = np.linalg.norm(u)
            norm_v = np.linalg.norm(v)
            if norm_u > 0 and norm_v > 0:
                cosine_dist = 1.0 - float(dot / (norm_u * norm_v))
                if cosine_dist <= threshold:
                    return res
        return None

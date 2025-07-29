# models/parking_spot.py

def get_db():
    from app import get_db as app_get_db
    return app_get_db()

class ParkingSpot:
    def __init__(self, row):
        self.id = row['id']
        self.lot_id = row['lot_id']
        self.status = row['status']

    @staticmethod
    def create(lot_id, status='A'):
        db = get_db()
        db.execute(
            'INSERT INTO parking_spots (lot_id, status) VALUES (?, ?)',
            (lot_id, status)
        )
        db.commit()
        row = db.execute(
            'SELECT * FROM parking_spots WHERE lot_id = ? AND status = ? ORDER BY id DESC LIMIT 1',
            (lot_id, status)
        ).fetchone()
        return ParkingSpot(row) if row else None

    @staticmethod
    def get_by_id(spot_id):
        db = get_db()
        row = db.execute('SELECT * FROM parking_spots WHERE id = ?', (spot_id,)).fetchone()
        return ParkingSpot(row) if row else None

    @staticmethod
    def get_available_by_lot(lot_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM parking_spots WHERE lot_id = ? AND status = 'A' LIMIT 1",
            (lot_id,)
        ).fetchone()
        return ParkingSpot(row) if row else None

    @staticmethod
    def get_all_by_lot(lot_id):
        db = get_db()
        rows = db.execute('SELECT * FROM parking_spots WHERE lot_id = ?', (lot_id,)).fetchall()
        return [ParkingSpot(row) for row in rows]

    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute('SELECT * FROM parking_spots').fetchall()
        return [ParkingSpot(row) for row in rows]

    @staticmethod
    def set_status(spot_id, status):
        db = get_db()
        db.execute(
            'UPDATE parking_spots SET status = ? WHERE id = ?',
            (status, spot_id)
        )
        db.commit()

    @staticmethod
    def count_occupied_by_lot(lot_id):
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) as count FROM parking_spots WHERE lot_id = ? AND status = 'O'",
            (lot_id,)
        ).fetchone()
        return row['count'] if row else 0

    @staticmethod
    def get_available_by_lot_limit(lot_id, limit):
        db = get_db()
        rows = db.execute(
            "SELECT * FROM parking_spots WHERE lot_id = ? AND status = 'A' LIMIT ?",
            (lot_id, limit)
        ).fetchall()
        return [ParkingSpot(row) for row in rows]

    @staticmethod
    def delete(spot_id):
        db = get_db()
        db.execute('DELETE FROM parking_spots WHERE id = ?', (spot_id,))
        db.commit()

from datetime import datetime

def get_db():
    from app import get_db
    return get_db()

class Reservation:
    def __init__(self, row):
        self.id = row['id']
        self.spot_id = row['spot_id']
        self.user_id = row['user_id']
        self.parking_timestamp = row['parking_timestamp']
        self.leaving_timestamp = row['leaving_timestamp']
        self.parking_cost = row['parking_cost']

    @staticmethod
    def create(spot_id, user_id):
        db = get_db()
        parking_timestamp = datetime.utcnow().isoformat()
        db.execute(
            'INSERT INTO reservations (spot_id, user_id, parking_timestamp) VALUES (?, ?, ?)',
            (spot_id, user_id, parking_timestamp)
        )
        db.commit()
        row = db.execute(
            'SELECT * FROM reservations WHERE spot_id = ? AND user_id = ? AND parking_timestamp = ?',
            (spot_id, user_id, parking_timestamp)
        ).fetchone()
        return Reservation(row)

    @staticmethod
    def get_by_id(reservation_id):
        db = get_db()
        row = db.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
        return Reservation(row) if row else None

    @staticmethod
    def get_by_user(user_id):
        db = get_db()
        rows = db.execute('SELECT * FROM reservations WHERE user_id = ?', (user_id,)).fetchall()
        return [Reservation(row) for row in rows]

    @staticmethod
    def release(reservation_id, parking_cost):
        db = get_db()
        leaving_timestamp = datetime.utcnow().isoformat()
        db.execute(
            'UPDATE reservations SET leaving_timestamp = ?, parking_cost = ? WHERE id = ?',
            (leaving_timestamp, parking_cost, reservation_id)
        )
        db.commit()

    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute('SELECT * FROM reservations').fetchall()
        return [Reservation(row) for row in rows]

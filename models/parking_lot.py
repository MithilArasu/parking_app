def get_db():
    from app import get_db
    return get_db()

class ParkingLot:
    def __init__(self, row):
        self.id = row['id']
        self.prime_location_name = row['prime_location_name']
        self.price = row['price']
        self.address = row['address']
        self.pin_code = row['pin_code']
        self.maximum_number_of_spots = row['maximum_number_of_spots']

    @staticmethod
    def create(name, price, address, pin_code, max_spots):
        db = get_db()
        db.execute(
            'INSERT INTO parking_lots (prime_location_name, price, address, pin_code, maximum_number_of_spots) VALUES (?, ?, ?, ?, ?)',
            (name, price, address, pin_code, max_spots)
        )
        db.commit()
        row = db.execute(
            'SELECT * FROM parking_lots WHERE prime_location_name = ? ORDER BY id DESC LIMIT 1',
            (name,)
        ).fetchone()
        return ParkingLot(row)

    @staticmethod
    def get_by_id(lot_id):
        db = get_db()
        row = db.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,)).fetchone()
        return ParkingLot(row) if row else None

    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute('SELECT * FROM parking_lots').fetchall()
        return [ParkingLot(row) for row in rows]

    @staticmethod
    def update(lot_id, name, price, address, pin_code, max_spots):
        db = get_db()
        db.execute(
            'UPDATE parking_lots SET prime_location_name = ?, price = ?, address = ?, pin_code = ?, maximum_number_of_spots = ? WHERE id = ?',
            (name, price, address, pin_code, max_spots, lot_id)
        )
        db.commit()

    @staticmethod
    def delete(lot_id):
        db = get_db()
        db.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
        db.commit()

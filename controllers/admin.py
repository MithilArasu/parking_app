from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from models import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    lots = ParkingLot.query.all()
    users = User.query.filter_by(is_admin=False).all()
    reservations = Reservation.query.all()
    return render_template('admin_dashboard.html', lots=lots, users=users, reservations=reservations)

@admin_bp.route('/admin/create_lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        name = request.form['prime_location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['maximum_number_of_spots'])
        lot = ParkingLot(prime_location_name=name, price=price, address=address, pin_code=pin_code, maximum_number_of_spots=max_spots)
        db.session.add(lot)
        db.session.commit()
        # Create spots
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        flash('Parking lot created!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('create_lot.html')

@admin_bp.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.price = float(request.form['price'])
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        new_max_spots = int(request.form['maximum_number_of_spots'])
        old_max_spots = lot.maximum_number_of_spots
        lot.maximum_number_of_spots = new_max_spots
        db.session.commit()
        # Adjust spots
        if new_max_spots > old_max_spots:
            for _ in range(new_max_spots - old_max_spots):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
        elif new_max_spots < old_max_spots:
            spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(old_max_spots - new_max_spots).all()
            for spot in spots:
                db.session.delete(spot)
        db.session.commit()
        flash('Parking lot updated!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_lot.html', lot=lot)

@admin_bp.route('/admin/delete_lot/<int:lot_id>', methods=['POST'])
@login_required
def delete_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occupied > 0:
        flash('Cannot delete lot with occupied spots.', 'danger')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted!', 'success')
    return redirect(url_for('admin.dashboard'))

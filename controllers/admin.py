from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    lots = ParkingLot.get_all()
    users = User.get_all_non_admin()
    reservations = Reservation.get_all()
    return render_template('admin_dashboard.html', lots=lots, users=users, reservations=reservations)

@admin_bp.route('/admin/create_lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        name = request.form['prime_location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['maximum_number_of_spots'])
        lot = ParkingLot.create(name, price, address, pin_code, max_spots)
        for _ in range(max_spots):
            ParkingSpot.create(lot.id, status='A')
        flash('Parking lot created!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('create_lot.html')

@admin_bp.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    lot = ParkingLot.get_by_id(lot_id)
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    if request.method == 'POST':
        name = request.form['prime_location_name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        new_max_spots = int(request.form['maximum_number_of_spots'])
        old_max_spots = lot.maximum_number_of_spots
        ParkingLot.update(lot_id, name, price, address, pin_code, new_max_spots)
        if new_max_spots > old_max_spots:
            for _ in range(new_max_spots - old_max_spots):
                ParkingSpot.create(lot_id, status='A')
        elif new_max_spots < old_max_spots:
            available_spots = ParkingSpot.get_available_by_lot_limit(lot_id, old_max_spots - new_max_spots)
            for spot in available_spots:
                ParkingSpot.delete(spot.id)
        flash('Parking lot updated!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('edit_lot.html', lot=lot)

@admin_bp.route('/admin/delete_lot/<int:lot_id>', methods=['POST'])
@login_required
def delete_lot(lot_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    lot = ParkingLot.get_by_id(lot_id)
    if not lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    occupied_count = ParkingSpot.count_occupied_by_lot(lot_id)
    if occupied_count > 0:
        flash('Cannot delete lot with occupied spots.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    ParkingLot.delete(lot_id)
    flash('Parking lot deleted!', 'success')
    return redirect(url_for('admin.admin_dashboard'))

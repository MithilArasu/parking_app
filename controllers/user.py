from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from datetime import datetime

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    lots = ParkingLot.get_all()
    reservations = Reservation.get_by_user(current_user.id)
    parking_spots = ParkingSpot.get_all()  # Make sure this is here!
    return render_template('user_dashboard.html', lots=lots, reservations=reservations, parking_spots=parking_spots)


@user_bp.route('/user/reserve/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def reserve(lot_id):
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    lot = ParkingLot.get_by_id(lot_id)
    spot = ParkingSpot.get_available_by_lot(lot_id)
    if not spot:
        flash('No available spots in this lot.', 'danger')
        return redirect(url_for('user.user_dashboard'))
    if request.method == 'POST':
        ParkingSpot.set_status(spot.id, 'O')
        Reservation.create(spot.id, current_user.id)
        flash('Spot reserved!', 'success')
        return redirect(url_for('user.user_dashboard'))
    return render_template('reserve.html', lot=lot, spot=spot)

@user_bp.route('/user/release/<int:reservation_id>', methods=['POST'])
@login_required
def release(reservation_id):
    reservation = Reservation.get_by_id(reservation_id)
    if not reservation or reservation.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('user.user_dashboard'))
    if reservation.leaving_timestamp is not None:
        flash('Already released!', 'info')
        return redirect(url_for('user.user_dashboard'))
    leaving_time = datetime.utcnow()
    parking_time = datetime.fromisoformat(reservation.parking_timestamp)
    duration = (leaving_time - parking_time).total_seconds() / 3600
    lot = ParkingLot.get_by_id(ParkingSpot.get_by_id(reservation.spot_id).lot_id)
    parking_cost = round(duration * lot.price, 2)
    Reservation.release(reservation.id, parking_cost)
    ParkingSpot.set_status(reservation.spot_id, 'A')
    flash(f'Spot released! Total cost: ₹{parking_cost}', 'success')
    return redirect(url_for('user.user_dashboard'))

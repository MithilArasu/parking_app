from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from models import db
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', lots=lots, reservations=reservations)

@user_bp.route('/user/reserve/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def reserve(lot_id):
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
    if not spot:
        flash('No available spots in this lot.', 'danger')
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        spot.status = 'O'
        reservation = Reservation(spot_id=spot.id, user_id=current_user.id, parking_timestamp=datetime.utcnow())
        db.session.add(reservation)
        db.session.commit()
        flash('Spot reserved!', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('reserve.html', lot=lot, spot=spot)

@user_bp.route('/user/release/<int:reservation_id>', methods=['POST'])
@login_required
def release(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('user.dashboard'))
    if reservation.leaving_timestamp is not None:
        flash('Already released!', 'info')
        return redirect(url_for('user.dashboard'))
    reservation.leaving_timestamp = datetime.utcnow()
    # Calculate cost
    duration = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    lot = reservation.spot.lot
    reservation.parking_cost = round(duration * lot.price, 2)
    reservation.spot.status = 'A'
    db.session.commit()
    flash(f'Spot released! Total cost: ₹{reservation.parking_cost}', 'success')
    return redirect(url_for('user.dashboard'))

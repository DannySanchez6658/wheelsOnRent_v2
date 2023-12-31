import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from car_app.customer import login_required
from car_app.db import get_db
from car_app.shared_variables import get_greeting

bp = Blueprint('car', __name__, url_prefix='/wheels_on_rent/car')

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Function to get the path for uploaded files
def get_upload_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

# Admin mode page, Admin can see all cars(booked and avalable)
@bp.route('/')
@login_required
def index():
    db = get_db()
    cars = db.execute(
        'SELECT id, name, model, seat, door, gearbox, image, price'
        ' FROM car'
        ' ORDER BY name ASC'
    ).fetchall()
    return render_template('admin/car_index.html', cars=cars)

# Car list
@bp.route('/available')
@login_required
def available():
    # Say Good Morning/Good Afternoon your customer
    greeting = get_greeting()

    # connect to database
    db = get_db()
    cars = db.execute(
        'SELECT id, name, model, seat, door, gearbox,  image, price'
        ' FROM car'
        ' WHERE status = 1'
        ' ORDER BY name ASC'
    ).fetchall()
    return render_template('car/index.html', greeting=greeting, cars=cars)

# Guest mode page, Customer can see without logging in if he wish
@bp.route('/guest_mode')
def guest_mode():
    guest = 1
    db = get_db()
    cars = db.execute(
        'SELECT id, name, model, seat, door, gearbox, image, price'
        ' FROM car'
        ' WHERE status = 1'
        ' ORDER BY name ASC'
    ).fetchall()
    return render_template('car/index.html', guest=guest, cars=cars)

## Admin can create new car entry ##
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        status = request.form['status']
        seat = request.form['seat']
        door = request.form['door']
        gearbox = request.form['gearbox']
        image = request.files['image']
        price = request.form['price']
        error = None

        if not name:
            error = 'Name is required.'
        if not model:
            error = 'Model is required.'
        if not status:
            error = 'Status is required.'
        if not seat:
            error = 'Seat is required.'
        if not door:
            error = 'Door is required.'
        if not gearbox:
            error = 'Gearbox is required.'
        if not price:
            error = 'Price is required.'

        if error is not None:
            flash(error)
        else:
            # Check if an image was uploaded
            if image and allowed_file(image.filename):
                image_data = image.read()  # Read the binary image data

                db = get_db()
                db.execute(
                    'INSERT INTO car (name, model, status, seat, door, gearbox, image, price)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (name, model, status, seat, door, gearbox, image_data, price)
                )
                db.commit()
                return redirect(url_for('car.index'))
            else:
                # Handle invalid or missing image
                flash('Invalid or missing image.')

    return render_template('admin/car_create.html')


# Getting a car associated with a given id to update it
def get_car(id, check_author=True):
    car = get_db().execute(
        'SELECT id, name, model, status, seat, door, gearbox, image, price'
        ' FROM car'
        ' WHERE car.id = ?',
        (id,)
    ).fetchone()

    if car is None:
        abort(404, f"Car id {id} doesn't exist.")

    return car

# Admin can update car details
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    car = get_car(id)

    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        status = request.form['status']
        seat = request.form['seat']
        door = request.form['door']
        gearbox = request.form['gearbox']
        image = request.files['image']
        price = request.form['price']
        error = None

        if not name:
            error = 'Name is required.'
        if not model:
            error = 'Model is required.'
        if not status:
            error = 'Status is required.'
        if not seat:
            error = 'Seat is required.'
        if not door:
            error = 'Door is required.'
        if not gearbox:
            error = 'Gearbox is required.'
        if not price:
            error = 'Price is required.'

        if error is not None:
            flash(error)
        else:
            # Check if an image was uploaded
            db = get_db()
            if image and allowed_file(image.filename):
                image_data = image.read() 

                db.execute(
                    'UPDATE car SET name = ?, model = ?, status = ?, seat = ?, door = ?, gearbox = ?, image = ?, price = ?'
                    'WHERE id = ?',
                    (name, model, status, seat, door, gearbox, image_data, price, id)
                )
            else:
                # Keep the previous image and update other car details
                db.execute(
                    'UPDATE car SET name = ?, model = ?, status = ?, seat = ?, door = ?, gearbox = ?, price = ?'
                    'WHERE id = ?',
                    (name, model, status, seat, door, gearbox, price, id)
                )
            db.commit()
            return redirect(url_for('car.index'))
    return render_template('admin/car_update.html', car=car)

# Deletes the car with a given id
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_car(id)
    db = get_db()
    db.execute('DELETE FROM car WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('car.index'))

# About us
@bp.route('/about')
def about():
    return render_template('car/about.html')

# Contact
@bp.route('/contact')
def contact():
    return render_template('car/contact.html')

# Service
@bp.route('/service')
def service():
    return render_template('car/service.html')

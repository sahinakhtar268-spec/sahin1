from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import string
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.units import inch

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    airline = db.Column(db.String(50), nullable=False)
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)
    price_economy = db.Column(db.Float, nullable=False)
    price_business = db.Column(db.Float, nullable=False)
    price_first = db.Column(db.Float, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pnr = db.Column(db.String(10), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_email = db.Column(db.String(120), nullable=False)
    passenger_phone = db.Column(db.String(20), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_class = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    booking_status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    flight = db.relationship('Flight', backref='bookings')
    user = db.relationship('User', backref='bookings')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_pnr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Sample cities
CITIES = [
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
    'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
    'London', 'Paris', 'Tokyo', 'Dubai', 'Singapore', 'Hong Kong',
    'Sydney', 'Mumbai', 'Delhi', 'Bangkok', 'Istanbul', 'Seoul'
]

AIRLINES = [
    'SkyWings Airlines', 'CloudHopper Airways', 'AeroConnect', 
    'JetStream Pacific', 'TransGlobal Air', 'SkyBridge International'
]

# Routes
@app.route('/')
def index():
    return render_template('index.html', cities=CITIES, airlines=AIRLINES)

@app.route('/search')
def search():
    return render_template('search_flights.html', cities=CITIES)

@app.route('/api/flights', methods=['POST'])
def api_flights():
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    date = request.form.get('date')
    passengers = int(request.form.get('passengers', 1))
    
    flights = Flight.query.filter(
        Flight.origin == origin,
        Flight.destination == destination,
        Flight.status == 'active',
        Flight.available_seats >= passengers
    ).all()
    
    return render_template('flight_results.html', flights=flights, passengers=passengers)

@app.route('/flight/<int:flight_id>')
def flight_details(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    return render_template('flight_details.html', flight=flight)

@app.route('/seats/<int:flight_id>')
def seat_selection(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    booked_seats = [b.seat_number for b in flight.bookings if b.booking_status != 'cancelled']
    return render_template('seat_selection.html', flight=flight, booked_seats=booked_seats)

@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def booking(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    
    if request.method == 'POST':
        passenger_name = request.form.get('passenger_name')
        passenger_email = request.form.get('passenger_email')
        passenger_phone = request.form.get('passenger_phone')
        seat_number = request.form.get('seat_number')
        seat_class = request.form.get('seat_class')
        
        if seat_class == 'economy':
            price = flight.price_economy
        elif seat_class == 'business':
            price = flight.price_business
        else:
            price = flight.price_first
        
        pnr = generate_pnr()
        
        user_id = current_user.id if current_user.is_authenticated else None
        
        booking = Booking(
            pnr=pnr,
            user_id=user_id,
            flight_id=flight.id,
            passenger_name=passenger_name,
            passenger_email=passenger_email,
            passenger_phone=passenger_phone,
            seat_number=seat_number,
            seat_class=seat_class,
            price=price
        )
        
        db.session.add(booking)
        flight.available_seats -= 1
        db.session.commit()
        
        flash('Booking confirmed! Your PNR is: ' + pnr, 'success')
        return redirect(url_for('ticket', pnr=pnr))
    
    return render_template('booking.html', flight=flight)

@app.route('/ticket/<pnr>')
def ticket(pnr):
    booking = Booking.query.filter_by(pnr=pnr).first_or_404()
    return render_template('ticket.html', booking=booking)

@app.route('/ticket/<pnr>/pdf')
def ticket_pdf(pnr):
    booking = Booking.query.filter_by(pnr=pnr).first_or_404()
    flight = booking.flight
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor('#1e3a5f')
    )
    
    # Heading Style
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.HexColor('#1e3a5f')
    )
    
    # Normal Style
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    # Header
    elements.append(Paragraph("✈️ SkyWings Airlines", title_style))
    elements.append(Paragraph("BOARDING PASS / TICKET", heading_style))
    elements.append(Paragraph("-" * 60, normal_style))
    elements.append(Paragraph("<br/>", normal_style))
    
    # PNR and Booking Info
    data = [
        ['PNR', 'BOOKING DATE', 'STATUS'],
        [booking.pnr, booking.created_at.strftime('%Y-%m-%d'), booking.booking_status.upper()]
    ]
    t = Table(data, colWidths=[2*inch, 2*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Paragraph("<br/>", normal_style))
    
    # Flight Details
    elements.append(Paragraph("FLIGHT DETAILS", heading_style))
    flight_data = [
        ['FLIGHT NO', 'AIRLINE', 'ORIGIN', 'DESTINATION'],
        [flight.flight_number, flight.airline, flight.origin, flight.destination],
        ['DEPARTURE', 'ARRIVAL', 'CLASS', 'SEAT'],
        [flight.departure_time, flight.arrival_time, booking.seat_class.upper(), booking.seat_number]
    ]
    ft = Table(flight_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(ft)
    elements.append(Paragraph("<br/>", normal_style))
    
    # Passenger Details
    elements.append(Paragraph("PASSENGER DETAILS", heading_style))
    passenger_data = [
        ['NAME', 'EMAIL', 'PHONE'],
        [booking.passenger_name, booking.passenger_email, booking.passenger_phone]
    ]
    pt = Table(passenger_data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ed8936')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(pt)
    elements.append(Paragraph("<br/>", normal_style))
    
    # Price
    price_data = [['TOTAL AMOUNT PAID'], [f"${booking.price:.2f}"]]
    price_table = Table(price_data, colWidths=[6*inch])
    price_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(price_table)
    
    # Footer
    elements.append(Paragraph("<br/><br/>", normal_style))
    elements.append(Paragraph("-" * 60, normal_style))
    elements.append(Paragraph("This is a computer generated ticket. Please carry a valid ID proof during check-in.", 
                               ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))
    elements.append(Paragraph("Thank you for choosing SkyWings Airlines!", 
                               ParagraphStyle('Thanks', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor('#1e3a5f'))))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'ticket_{pnr}.pdf', mimetype='application/pdf')

# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password, phone=phone)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    total_flights = Flight.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.price)).scalar() or 0
    active_users = User.query.count()
    
    # Get booking stats for chart
    bookings_by_month = []
    for i in range(6):
        month = datetime.utcnow() - timedelta(days=30*i)
        count = Booking.query.filter(
            db.extract('month', Booking.created_at) == month.month
        ).count()
        bookings_by_month.append(count)
    bookings_by_month.reverse()
    
    # Get airline revenue
    airline_revenue = []
    for airline in AIRLINES:
        revenue = db.session.query(db.func.sum(Booking.price)).join(Flight).filter(Flight.airline == airline).scalar() or 0
        airline_revenue.append(revenue)
    
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                         total_flights=total_flights,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         active_users=active_users,
                         bookings_by_month=bookings_by_month,
                         airline_revenue=airline_revenue,
                         recent_bookings=recent_bookings,
                         airlines=AIRLINES)

@app.route('/admin/flights')
def manage_flights():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    flights = Flight.query.order_by(Flight.created_at.desc()).all()
    return render_template('manage_flights.html', flights=flights, cities=CITIES, airlines=AIRLINES)

@app.route('/admin/flights/add', methods=['POST'])
def add_flight():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    flight = Flight(
        flight_number=request.form.get('flight_number'),
        airline=request.form.get('airline'),
        origin=request.form.get('origin'),
        destination=request.form.get('destination'),
        departure_time=request.form.get('departure_time'),
        arrival_time=request.form.get('arrival_time'),
        price_economy=float(request.form.get('price_economy')),
        price_business=float(request.form.get('price_business')),
        price_first=float(request.form.get('price_first')),
        total_seats=int(request.form.get('total_seats')),
        available_seats=int(request.form.get('total_seats'))
    )
    
    db.session.add(flight)
    db.session.commit()
    flash('Flight added successfully!', 'success')
    return redirect(url_for('manage_flights'))

@app.route('/admin/flights/<int:id>/edit', methods=['POST'])
def edit_flight(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    flight = Flight.query.get_or_404(id)
    flight.flight_number = request.form.get('flight_number')
    flight.airline = request.form.get('airline')
    flight.origin = request.form.get('origin')
    flight.destination = request.form.get('destination')
    flight.departure_time = request.form.get('departure_time')
    flight.arrival_time = request.form.get('arrival_time')
    flight.price_economy = float(request.form.get('price_economy'))
    flight.price_business = float(request.form.get('price_business'))
    flight.price_first = float(request.form.get('price_first'))
    flight.status = request.form.get('status')
    
    db.session.commit()
    flash('Flight updated successfully!', 'success')
    return redirect(url_for('manage_flights'))

@app.route('/admin/flights/<int:id>/delete')
def delete_flight(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    flight = Flight.query.get_or_404(id)
    db.session.delete(flight)
    db.session.commit()
    flash('Flight deleted successfully!', 'success')
    return redirect(url_for('manage_flights'))

@app.route('/admin/bookings')
def manage_bookings():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('manage_bookings.html', bookings=bookings)

@app.route('/admin/bookings/<int:id>/cancel')
def cancel_booking(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    booking = Booking.query.get_or_404(id)
    booking.booking_status = 'cancelled'
    
    flight = booking.flight
    flight.available_seats += 1
    
    db.session.commit()
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('manage_bookings'))

@app.route('/admin/passengers')
def passengers():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('passengers.html', bookings=bookings)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Initialize database with sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample flights if none exist
        if Flight.query.count() == 0:
            sample_flights = [
                Flight(flight_number='SW101', airline='SkyWings Airlines', origin='New York', 
                       destination='London', departure_time='08:00', arrival_time='20:00',
                       price_economy=450, price_business=1200, price_first=2500, total_seats=180, available_seats=180),
                Flight(flight_number='SW102', airline='SkyWings Airlines', origin='Los Angeles', 
                       destination='Tokyo', departure_time='10:00', arrival_time='14:00+1',
                       price_economy=650, price_business=1800, price_first=3500, total_seats=150, available_seats=150),
                Flight(flight_number='CH201', airline='CloudHopper Airways', origin='Chicago', 
                       destination='Paris', departure_time='14:00', arrival_time='06:00+1',
                       price_economy=520, price_business=1400, price_first=2800, total_seats=120, available_seats=120),
                Flight(flight_number='AC301', airline='AeroConnect', origin='Houston', 
                       destination='Dubai', departure_time='18:00', arrival_time='16:00+1',
                       price_economy=700, price_business=2000, price_first=4000, total_seats=200, available_seats=200),
                Flight(flight_number='JP401', airline='JetStream Pacific', origin='San Francisco', 
                       destination='Singapore', departure_time='22:00', arrival_time='06:00+2',
                       price_economy=580, price_business=1600, price_first=3200, total_seats=160, available_seats=160),
                Flight(flight_number='TG501', airline='TransGlobal Air', origin='Miami', 
                       destination='Sydney', departure_time='21:00', arrival_time='07:00+2',
                       price_economy=750, price_business=2200, price_first=4500, total_seats=140, available_seats=140),
                Flight(flight_number='SB601', airline='SkyBridge International', origin='Boston', 
                       destination='Hong Kong', departure_time='23:00', arrival_time='06:00+2',
                       price_economy=620, price_business=1750, price_first=3400, total_seats=130, available_seats=130),
                Flight(flight_number='SW202', airline='SkyWings Airlines', origin='Seattle', 
                       destination='Mumbai', departure_time='16:00', arrival_time='18:00+1',
                       price_economy=680, price_business=1900, price_first=3800, total_seats=170, available_seats=170),
            ]
            
            db.session.bulk_save_objects(sample_flights)
            db.session.commit()
            print("Sample flights added!")
        
        # Add sample admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@skywings.com',
                password=generate_password_hash('admin123'),
                phone='1234567890'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


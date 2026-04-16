# Advanced Online Air Ticketing Reservation System - Specification

## 1. Project Overview

**Project Name:** Advanced Online Air Ticketing Reservation System
**Project Type:** Full-stack Web Application
**Core Functionality:** A modern airline booking system allowing users to search flights, select seats, book tickets, generate PDF tickets, and manage bookings through an admin dashboard.
**Target Users:** Airline passengers and airline administrators

## 2. Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Chart.js (for dashboard charts)

### Backend
- Python Flask
- Flask-SQLAlchemy
- Flask-Login

### Database
- SQLite

### Libraries
- Flask
- ReportLab (PDF generation)
- SQLite3

## 3. UI/UX Specification

### Color Palette
- **Primary:** #1e3a5f (Deep Navy Blue)
- **Secondary:** #2c5282 (Medium Blue)
- **Accent:** #ed8936 (Orange - for CTAs)
- **Success:** #38a169 (Green)
- **Danger:** #e53e3e (Red)
- **Background:** #f7fafc (Light Gray)
- **Card Background:** #ffffff (White)
- **Text Primary:** #2d3748 (Dark Gray)
- **Text Secondary:** #718096 (Medium Gray)

### Typography
- **Headings:** 'Poppins', sans-serif (weights: 600, 700)
- **Body:** 'Open Sans', sans-serif (weights: 400, 600)
- **Logo/Brand:** 'Poppins', sans-serif (weight: 700)

### Font Sizes
- H1: 2.5rem
- H2: 2rem
- H3: 1.5rem
- Body: 1rem
- Small: 0.875rem

### Spacing System
- Base unit: 0.25rem
- Section padding: 4rem 0
- Card padding: 1.5rem
- Component margin: 1rem

### Responsive Breakpoints
- Mobile: < 576px
- Tablet: 576px - 992px
- Desktop: > 992px

## 4. Page Structure

### 4.1 Public Pages

#### Home Page (index.html)
- Navigation bar with logo, search flights, login, register links
- Hero section with flight search form
- Features section showing system capabilities
- Statistics section with animated counters
- Footer with links and copyright

#### Flight Search Page (search_flights.html)
- Search form: origin, destination, date, passengers
- Flight results displayed in cards
- Airline logo, flight number, departure/arrival times
- Price display with "Book Now" button

#### Seat Selection Page (seat_selection.html)
- Visual seat map with rows and columns
- Seat categories: Economy, Business, First Class
- Seat colors: Available (green), Selected (orange), Occupied (gray)
- Price display based on seat class
- Continue button to booking

#### Booking Page (booking.html)
- Passenger information form
- Contact details
- Booking summary
- Payment simulation
- Confirm booking button

#### Ticket Page (ticket.html)
- Ticket confirmation details
- Passenger information
- Flight details
- Seat information
- Download PDF button

#### User Login/Register Pages
- Clean forms with validation
- Remember me option
- Social login placeholders

### 4.2 Admin Pages

#### Admin Login (admin_login.html)
- Username/password form
- Secure login

#### Admin Dashboard (admin_dashboard.html)
- Statistics cards: Total Flights, Total Bookings, Total Revenue, Active Users
- Charts: Booking trends, Popular routes
- Recent bookings table
- Quick actions

#### Flight Management (manage_flights.html)
- Flight list with search/filter
- Add new flight form
- Edit/Delete flight actions
- Flight status toggle

#### Booking Management (manage_bookings.html)
- All bookings table
- Filter by status, date, flight
- View booking details
- Cancel booking option

#### Passenger List (passengers.html)
- All passengers table
- Search by name, PNR
- View passenger details

## 5. Database Schema

### Tables

#### users
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- email (TEXT UNIQUE)
- password (TEXT)
- phone (TEXT)
- created_at (TIMESTAMP)

#### flights
- id (INTEGER PRIMARY KEY)
- flight_number (TEXT UNIQUE)
- airline (TEXT)
- origin (TEXT)
- destination (TEXT)
- departure_time (TEXT)
- arrival_time (TEXT)
- price_economy (REAL)
- price_business (REAL)
- price_first (REAL)
- total_seats (INTEGER)
- available_seats (INTEGER)
- status (TEXT DEFAULT 'active')
- created_at (TIMESTAMP)

#### bookings
- id (INTEGER PRIMARY KEY)
- pnr (TEXT UNIQUE)
- user_id (INTEGER FOREIGN KEY)
- flight_id (INTEGER FOREIGN KEY)
- passenger_name (TEXT)
- passenger_email (TEXT)
- passenger_phone (TEXT)
- seat_number (TEXT)
- seat_class (TEXT)
- price (REAL)
- booking_status (TEXT DEFAULT 'confirmed')
- created_at (TIMESTAMP)

## 6. Functionality Specification

### User Features

#### Flight Search
- Form validation for all fields
- Date picker with minimum date (today)
- Passenger count (1-9)
- Results sorted by price (default)
- Filter by airline, price range

#### Seat Selection
- Interactive seat map
- Real-time seat availability
- Multiple seat class sections
- Seat price calculation
- Maximum 4 seats per booking

#### Booking Process
- Passenger details form
- Contact information
- Price calculation
- PNR generation (6 random characters)
- Confirmation email simulation

#### PDF Ticket Generation
- Professional ticket layout
- QR code placeholder
- All booking details
- Airline branding
- Downloadable PDF

### Admin Features

#### Authentication
- Secure admin login
- Session management
- Logout functionality

#### Flight Management
- CRUD operations for flights
- Set flight status (active/cancelled)
- View flight details
- Automatic seat availability

#### Booking Management
- View all bookings
- Filter by various criteria
- Update booking status
- Cancel bookings

#### Dashboard Analytics
- Total statistics
- Booking trends chart (line chart)
- Revenue by airline (pie chart)
- Recent bookings list

## 7. API Endpoints

### User Routes
- GET / - Home page
- GET /search - Flight search page
- POST /api/flights - Search flights
- GET /flight/<id> - Flight details
- GET /seats/<flight_id> - Seat selection page
- POST /api/book - Create booking
- GET /ticket/<pnr> - View ticket
- GET /ticket/<pnr>/pdf - Download PDF

### Admin Routes
- GET /admin - Admin dashboard
- GET /admin/login - Admin login
- POST /admin/login - Process login
- GET /admin/flights - Manage flights
- POST /admin/flights/add - Add flight
- POST /admin/flights/<id>/edit - Edit flight
- POST /admin/flights/<id>/delete - Delete flight
- GET /admin/bookings - Manage bookings
- POST /admin/bookings/<id>/cancel - Cancel booking
- GET /admin/passengers - View passengers

## 8. Acceptance Criteria

### User Features
- [ ] User can search for flights with origin, destination, date
- [ ] User can view available flights with prices
- [ ] User can select seats from visual seat map
- [ ] User can complete booking with passenger details
- [ ] User receives PNR confirmation
- [ ] User can download PDF ticket

### Admin Features
- [ ] Admin can login securely
- [ ] Admin can view dashboard with statistics
- [ ] Admin can add/edit/delete flights
- [ ] Admin can view all bookings
- [ ] Admin can cancel bookings
- [ ] Admin can view passenger list

### UI/UX
- [ ] Responsive design works on all devices
- [ ] Modern airline-style interface
- [ ] Smooth animations and transitions
- [ ] Professional color scheme
- [ ] Intuitive navigation

### Technical
- [ ] Database properly initialized with sample data
- [ ] All forms have validation
- [ ] Error handling in place
- [ ] Session management works correctly
- [ ] PDF generation works correctly


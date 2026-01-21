"""
SafiWash CRM - Car Wash Customer Relationship Management System
================================================================
Author: Muthomi Manasseh
Institution: ZETECH UNIVERSITY
Date: MARCH 2026

System Overview:
----------------
This system addresses the problem of managing customer relationships in a car wash business.
The manager currently has no way to track regular customers, their visit frequency, or 
implement a loyalty reward program.

Core Modules:
1. Customer Management - Register and manage customer profiles
2. Visit Tracking - Log each service visit with details
3. Service Catalog - Define available services and pricing
4. Loyalty Program - Automatic reward tracking (10 visits = 1 free wash)
5. Revenue Analytics - Daily, weekly, and monthly income reports
6. Search and Filter - Quick customer lookup by phone or plate number

Technical Stack:
- Backend: Flask (Python Web Framework)
- Database: SQLite (Lightweight relational database)
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Bootstrap 5 (Responsive design)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_safiwash_key_2026')
DB_NAME = 'car_wash.db'

# Loyalty threshold - number of visits required for a free wash
LOYALTY_THRESHOLD = 10

@app.context_processor
def inject_now():
    return {
        'now': datetime.now,
        'user': session.get('user')
    }


def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Row factory allows accessing columns by name (e.g., row['name']).
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database schema with all required tables.
    This function runs once when the application starts.
    
    Tables:
    - customers: Stores customer profile information
    - services: Defines available wash services and prices
    - visits: Logs every customer visit with service details
    """
    conn = get_db_connection()
    with conn:
        # Customers Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                plate_number TEXT NOT NULL,
                car_model TEXT,
                total_visits INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0.0,
                loyalty_points INTEGER DEFAULT 0,
                joined_date TEXT NOT NULL,
                last_visit TEXT,
                notes TEXT
            )
        ''')
        
        # Services Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                duration_minutes INTEGER DEFAULT 30,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Visits Table (Transaction Log)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                visit_date TEXT NOT NULL,
                visit_time TEXT NOT NULL,
                amount_paid REAL NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                is_loyalty_reward INTEGER DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (service_id) REFERENCES services (id)
            )
        ''')

        # Users Table (For Auth)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'manager'
            )
        ''')
        
        # Add default admin user if not exists
        admin_username = os.getenv('ADMIN_USERNAME', 'CRM Mng')
        admin_password = os.getenv('ADMIN_PASSWORD', 'crmflow')
        
        admin = conn.execute('SELECT * FROM users WHERE username = ?', (admin_username,)).fetchone()
        if not admin:
            # Also check if the old 'admin' user exists and rename it, or just create new
            old_admin = conn.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
            if old_admin:
                conn.execute('UPDATE users SET username = ?, password = ?, full_name = ? WHERE username = "admin"',
                            (admin_username, generate_password_hash(admin_password), 'System Manager'))
            else:
                hashed_pw = generate_password_hash(admin_password)
                conn.execute('INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)',
                            (admin_username, hashed_pw, 'System Manager', 'admin'))
        
        # Insert default services if table is empty
        existing = conn.execute('SELECT COUNT(*) FROM services').fetchone()[0]
        if existing == 0:
            default_services = [
                ('Basic Exterior Wash', 'Quick exterior rinse and dry', 200.00, 15),
                ('Standard Wash', 'Exterior wash with interior vacuum', 350.00, 30),
                ('Full Service Wash', 'Complete exterior and interior cleaning', 500.00, 45),
                ('Premium Detail', 'Full wash plus wax and tire shine', 800.00, 60),
                ('Interior Deep Clean', 'Seats, dashboard, and carpet cleaning', 600.00, 50),
                ('Engine Bay Cleaning', 'Engine compartment wash and degrease', 400.00, 25)
            ]
            conn.executemany(
                'INSERT INTO services (name, description, price, duration_minutes) VALUES (?, ?, ?, ?)',
                default_services
            )
    conn.close()


# =============================================================================
# AUTHENTICATION DECORATOR
# =============================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access the system.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# ROUTES: AUTHENTICATION
# =============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user'] = {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role']
            }
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        new_password = request.form.get('new_password')
        
        if new_password:
            hashed_pw = generate_password_hash(new_password)
            conn.execute('UPDATE users SET full_name = ?, password = ? WHERE id = ?',
                        (full_name, hashed_pw, user_id))
        else:
            conn.execute('UPDATE users SET full_name = ? WHERE id = ?',
                        (full_name, user_id))
        
        conn.commit()
        # Update session info
        session['user']['full_name'] = full_name
        flash('Profile updated successfully.', 'success')
        
    conn.close()
    return render_template('profile.html', user=user)


# =============================================================================
# UTILITY FUNCTIONS: DASHBOARD ANALYTICS
# =============================================================================
def get_dashboard_stats():
    """
    Calculates key business metrics for the dashboard display.
    Returns dictionary with total customers, today's visits, revenue stats.
    """
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    month_start = datetime.now().strftime('%Y-%m-01')
    
    # At-risk customers (haven't visited in 14+ days)
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    at_risk_count = conn.execute(
        'SELECT COUNT(*) FROM customers WHERE last_visit < ? AND last_visit IS NOT NULL', (two_weeks_ago,)
    ).fetchone()[0]
    
    # Calculate potential lost revenue (average visit price * number of at-risk customers)
    avg_price = conn.execute('SELECT AVG(price) FROM services WHERE is_active = 1').fetchone()[0] or 350
    lost_revenue = at_risk_count * avg_price

    stats = {
        'total_customers': conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0],
        'visits_today': conn.execute(
            'SELECT COUNT(*) FROM visits WHERE visit_date = ?', (today,)
        ).fetchone()[0],
        'revenue_today': conn.execute(
            'SELECT COALESCE(SUM(amount_paid), 0) FROM visits WHERE visit_date = ?', (today,)
        ).fetchone()[0],
        'revenue_week': conn.execute(
            'SELECT COALESCE(SUM(amount_paid), 0) FROM visits WHERE visit_date >= ?', (week_ago,)
        ).fetchone()[0],
        'revenue_month': conn.execute(
            'SELECT COALESCE(SUM(amount_paid), 0) FROM visits WHERE visit_date >= ?', (month_start,)
        ).fetchone()[0],
        'loyalty_due': conn.execute(
            'SELECT COUNT(*) FROM customers WHERE loyalty_points >= ?', (LOYALTY_THRESHOLD,)
        ).fetchone()[0],
        'at_risk_count': at_risk_count,
        'lost_revenue': lost_revenue
    }
    conn.close()
    return stats


# =============================================================================
# ROUTES: DASHBOARD
# =============================================================================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard view displaying key business metrics.
    Shows: Total customers, today's visits, revenue summary, recent activity.
    """
    conn = get_db_connection()
    stats = get_dashboard_stats()
    
    # Get recent visits with customer and service details
    recent_visits = conn.execute('''
        SELECT v.*, c.name as customer_name, c.plate_number, s.name as service_name
        FROM visits v
        JOIN customers c ON v.customer_id = c.id
        JOIN services s ON v.service_id = s.id
        ORDER BY v.id DESC
        LIMIT 10
    ''').fetchall()
    
    # Get top customers by total spent
    top_customers = conn.execute('''
        SELECT * FROM customers 
        ORDER BY total_spent DESC 
        LIMIT 5
    ''').fetchall()

    # Get at-risk customers (no visit in 14 days)
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    at_risk_customers = conn.execute('''
        SELECT *, (julianday('now') - julianday(last_visit)) as days_gone 
        FROM customers 
        WHERE last_visit < ? AND last_visit IS NOT NULL
        ORDER BY days_gone DESC
        LIMIT 10
    ''', (two_weeks_ago,)).fetchall()
    
    conn.close()
    
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_visits=recent_visits,
        top_customers=top_customers,
        at_risk_customers=at_risk_customers
    )


# =============================================================================
# ROUTES: CUSTOMER MANAGEMENT
# =============================================================================
@app.route('/customers')
@login_required
def customers():
    """
    Displays the customer database with search and filter capability.
    Customers are sorted by loyalty points (most loyal first).
    """
    conn = get_db_connection()
    
    # Handle search query
    search = request.args.get('search', '')
    if search:
        query = '''
            SELECT * FROM customers 
            WHERE name LIKE ? OR phone LIKE ? OR plate_number LIKE ?
            ORDER BY total_visits DESC
        '''
        search_term = f'%{search}%'
        all_customers = conn.execute(query, (search_term, search_term, search_term)).fetchall()
    else:
        all_customers = conn.execute('SELECT * FROM customers ORDER BY total_visits DESC').fetchall()
    
    conn.close()
    
    return render_template(
        'customers.html', 
        customers=all_customers,
        search=search,
        loyalty_threshold=LOYALTY_THRESHOLD
    )


@app.route('/customer/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    """
    Displays detailed profile for a single customer.
    Shows: Full info, visit history, loyalty status, spending summary.
    """
    conn = get_db_connection()
    
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers'))
    
    # Get visit history for this customer
    visits = conn.execute('''
        SELECT v.*, s.name as service_name
        FROM visits v
        JOIN services s ON v.service_id = s.id
        WHERE v.customer_id = ?
        ORDER BY v.id DESC
    ''', (customer_id,)).fetchall()
    
    conn.close()
    
    return render_template(
        'customer_detail.html',
        customer=customer,
        visits=visits,
        loyalty_threshold=LOYALTY_THRESHOLD
    )


@app.route('/customer/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    """
    Handles new customer registration.
    GET: Displays the registration form.
    POST: Processes the form and creates the customer record.
    """
    if request.method == 'POST':
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        plate = request.form['plate_number'].upper().strip()
        car_model = request.form.get('car_model', '').strip()
        notes = request.form.get('notes', '').strip()
        joined_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO customers (name, phone, plate_number, car_model, notes, joined_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, plate, car_model, notes, joined_date))
            conn.commit()
            flash(f'Customer "{name}" registered successfully.', 'success')
            return redirect(url_for('customers'))
        except sqlite3.IntegrityError:
            flash('A customer with this phone number already exists.', 'danger')
        finally:
            conn.close()
    
    return render_template('add_customer.html')


@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    """
    Handles customer profile updates.
    """
    conn = get_db_connection()
    customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers'))
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        plate = request.form['plate_number'].upper().strip()
        car_model = request.form.get('car_model', '').strip()
        notes = request.form.get('notes', '').strip()
        
        try:
            conn.execute('''
                UPDATE customers 
                SET name = ?, phone = ?, plate_number = ?, car_model = ?, notes = ?
                WHERE id = ?
            ''', (name, phone, plate, car_model, notes, customer_id))
            conn.commit()
            flash('Customer updated successfully.', 'success')
            return redirect(url_for('customer_detail', customer_id=customer_id))
        except sqlite3.IntegrityError:
            flash('Phone number already in use by another customer.', 'danger')
        finally:
            conn.close()
    
    conn.close()
    return render_template('edit_customer.html', customer=customer)


@app.route('/customer/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    """
    Deletes a customer and their visit history.
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM visits WHERE customer_id = ?', (customer_id,))
    conn.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    conn.close()
    flash('Customer and history deleted successfully.', 'success')
    return redirect(url_for('customers'))


# =============================================================================
# ROUTES: CHECK-IN (VISIT LOGGING)
# =============================================================================
@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    """
    Handles customer check-in process.
    Step 1: Search for customer by phone or plate.
    Step 2: Select service.
    Step 3: Confirm and log the visit.
    """
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services WHERE is_active = 1').fetchall()
    
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        service_id = request.form.get('service_id')
        payment_method = request.form.get('payment_method', 'Cash')
        is_loyalty_reward = request.form.get('is_loyalty_reward', '0') == '1'
        
        if not customer_id or not service_id:
            flash('Please select a customer and service.', 'warning')
            conn.close()
            return redirect(url_for('checkin'))
        
        # Get service price
        service = conn.execute('SELECT * FROM services WHERE id = ?', (service_id,)).fetchone()
        customer = conn.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
        
        if not service or not customer:
            flash('Invalid customer or service.', 'danger')
            conn.close()
            return redirect(url_for('checkin'))
        
        # Calculate amount (0 if loyalty reward)
        amount = 0.0 if is_loyalty_reward else service['price']
        today = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now().strftime('%H:%M:%S')
        
        # Insert visit record
        conn.execute('''
            INSERT INTO visits (customer_id, service_id, amount_paid, payment_method, is_loyalty_reward, visit_date, visit_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, service_id, amount, payment_method, 1 if is_loyalty_reward else 0, today, now))
        
        # Update customer stats
        new_points = 0 if is_loyalty_reward else customer['loyalty_points'] + 1
        if is_loyalty_reward:
            new_points = customer['loyalty_points'] - LOYALTY_THRESHOLD
            if new_points < 0:
                new_points = 0
        
        conn.execute('''
            UPDATE customers 
            SET total_visits = total_visits + 1,
                total_spent = total_spent + ?,
                loyalty_points = ?,
                last_visit = ?
            WHERE id = ?
        ''', (amount, new_points, today, customer_id))
        
        conn.commit()
        
        if is_loyalty_reward:
            flash(f'Loyalty reward redeemed for {customer["name"]}. Free wash applied.', 'info')
        else:
            flash(f'Check-in complete for {customer["name"]}. Amount: KES {amount:.2f}', 'success')
        
        conn.close()
        return redirect(url_for('dashboard'))
    
    customers = conn.execute('SELECT * FROM customers ORDER BY name').fetchall()
    conn.close()
    
    return render_template('checkin.html', services=services, customers=customers, loyalty_threshold=LOYALTY_THRESHOLD)


# =============================================================================
# ROUTES: SERVICES MANAGEMENT
# =============================================================================
@app.route('/services')
@login_required
def services():
    """
    Displays the service catalog with pricing.
    """
    conn = get_db_connection()
    all_services = conn.execute('SELECT * FROM services ORDER BY price').fetchall()
    conn.close()
    return render_template('services.html', services=all_services)


@app.route('/service/add', methods=['GET', 'POST'])
@login_required
def add_service():
    """
    Adds a new service to the catalog.
    """
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        price = float(request.form['price'])
        duration = int(request.form.get('duration_minutes', 30))
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO services (name, description, price, duration_minutes)
            VALUES (?, ?, ?, ?)
        ''', (name, description, price, duration))
        conn.commit()
        conn.close()
        
        flash(f'Service "{name}" added successfully.', 'success')
        return redirect(url_for('services'))
    
    return render_template('add_service.html')


@app.route('/service/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    """
    Updates an existing service.
    """
    conn = get_db_connection()
    service = conn.execute('SELECT * FROM services WHERE id = ?', (service_id,)).fetchone()
    
    if not service:
        conn.close()
        flash('Service not found.', 'danger')
        return redirect(url_for('services'))
        
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        price = float(request.form['price'])
        duration = int(request.form.get('duration_minutes', 30))
        
        conn.execute('''
            UPDATE services 
            SET name = ?, description = ?, price = ?, duration_minutes = ?
            WHERE id = ?
        ''', (name, description, price, duration, service_id))
        conn.commit()
        conn.close()
        
        flash(f'Service "{name}" updated successfully.', 'success')
        return redirect(url_for('services'))
    
    conn.close()
    return render_template('edit_service.html', service=service)


@app.route('/service/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service(service_id):
    """
    Deletes a service from the catalog.
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()
    flash('Service deleted successfully.', 'success')
    return redirect(url_for('services'))


# =============================================================================
# ROUTES: REPORTS
# =============================================================================
@app.route('/reports')
@login_required
def reports():
    """
    Displays financial and operational reports.
    """
    conn = get_db_connection()
    
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    month_start = datetime.now().strftime('%Y-%m-01')
    
    # Revenue by service type
    revenue_by_service = conn.execute('''
        SELECT s.name as service_name, COUNT(v.id) as visit_count, SUM(v.amount_paid) as total_revenue
        FROM visits v
        JOIN services s ON v.service_id = s.id
        GROUP BY s.id
        ORDER BY total_revenue DESC
    ''').fetchall()
    
    # Daily revenue for the past 7 days
    revenue_daily = conn.execute('''
        SELECT visit_date, COUNT(*) as visit_count, SUM(amount_paid) as total_revenue
        FROM visits
        WHERE visit_date >= ?
        GROUP BY visit_date
        ORDER BY visit_date DESC
    ''', (week_ago,)).fetchall()
    
    # Loyalty stats
    eligible_count = conn.execute(
        'SELECT COUNT(*) FROM customers WHERE loyalty_points >= ?', (LOYALTY_THRESHOLD,)
    ).fetchone()[0]
    
    avg_points = conn.execute(
        'SELECT AVG(loyalty_points) FROM customers'
    ).fetchone()[0] or 0
    
    loyalty_stats = {
        'eligible_count': eligible_count,
        'avg_points': avg_points
    }
    
    conn.close()
    
    return render_template(
        'reports.html',
        revenue_by_service=revenue_by_service,
        revenue_daily=revenue_daily,
        loyalty_stats=loyalty_stats,
        loyalty_threshold=LOYALTY_THRESHOLD
    )


# =============================================================================
# API ENDPOINTS (For AJAX calls)
# =============================================================================
@app.route('/api/customer/search')
@login_required
def api_search_customer():
    """
    API endpoint for quick customer search.
    Used by the check-in form for autocomplete.
    """
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = conn.execute('''
        SELECT id, name, phone, plate_number, loyalty_points
        FROM customers
        WHERE name LIKE ? OR phone LIKE ? OR plate_number LIKE ?
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in results])


# =============================================================================
# APPLICATION ENTRY POINT: SERVER BOOTSTRAP
# =============================================================================
if __name__ == '__main__':
    # Initialize the SQLite database schema if it doesn't exist
    init_db()
    # Start the Flask development server on port 5000
    app.run(debug=True, port=5000)

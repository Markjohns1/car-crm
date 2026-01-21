# SafiWash CRM
## Car Wash Customer Relationship Management System

### Project Overview
SafiWash CRM is a web-based application designed to help car wash businesses manage their customers, track visits, implement a loyalty reward program, and analyze revenue.

### Problem Statement
A small car wash business has a problem with managing its customers. They have many regular customers, but the manager has no easy way to keep a record of who they are, how often they visit, or to offer them a loyalty reward for their business.

### Solution
This system provides:
1. **Customer Management** - Register and maintain customer profiles with contact details and vehicle information
2. **Visit Tracking** - Log each service visit with date, time, service type, and payment method
3. **Loyalty Program** - Automatic reward tracking (10 visits = 1 free wash)
4. **Service Catalog** - Define available wash services with pricing and duration
5. **Revenue Reports** - Daily, weekly, and monthly income analysis
6. **Search Functionality** - Quick customer lookup by name, phone, or plate number

### Technical Stack
- **Backend**: Flask (Python Web Framework)
- **Database**: SQLite (Lightweight relational database)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5 (Responsive design)

### Project Structure
```
car-crm/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── car_wash.db         # SQLite database (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── main.js     # JavaScript functionality
└── templates/
    ├── base.html           # Base template with sidebar
    ├── dashboard.html      # Main dashboard
    ├── customers.html      # Customer list
    ├── customer_detail.html# Individual customer profile
    ├── add_customer.html   # New customer form
    ├── edit_customer.html  # Edit customer form
    ├── checkin.html        # Check-in process
    ├── services.html       # Service catalog
    ├── add_service.html    # Add new service form
    └── reports.html        # Financial reports
```

### Installation
1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open browser and navigate to: `http://127.0.0.1:5000`

### Features

#### Dashboard
- Total customer count
- Visits logged today
- Revenue summary (daily, weekly, monthly)
- Recent activity log
- Top customers by spending

#### Customer Management
- Add new customers with name, phone, plate number, car model
- Search customers by any field
- View individual customer profiles with visit history
- Edit customer information

#### Check-In System
- Select customer from dropdown
- Choose service type
- Select payment method (Cash, M-Pesa, Card)
- Apply loyalty reward when eligible

#### Loyalty Program
- Customers earn 1 point per paid visit
- After 10 visits, customer qualifies for a free wash
- Visual progress bar shows loyalty status
- System alerts when free wash is available

#### Reports
- Revenue breakdown by service type
- Daily revenue for the past 7 days
- Loyalty program statistics

### Database Schema

#### Customers Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Customer name |
| phone | TEXT | Phone number (unique) |
| plate_number | TEXT | Vehicle plate |
| car_model | TEXT | Vehicle model |
| total_visits | INTEGER | Cumulative visits |
| total_spent | REAL | Cumulative spending |
| loyalty_points | INTEGER | Current loyalty points |
| joined_date | TEXT | Registration date |
| last_visit | TEXT | Most recent visit |
| notes | TEXT | Additional notes |

#### Services Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Service name |
| description | TEXT | Service description |
| price | REAL | Price in KES |
| duration_minutes | INTEGER | Estimated duration |
| is_active | INTEGER | Active status |

#### Visits Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| customer_id | INTEGER | Foreign key to customers |
| service_id | INTEGER | Foreign key to services |
| amount_paid | REAL | Amount charged |
| payment_method | TEXT | Cash/M-Pesa/Card |
| is_loyalty_reward | INTEGER | Free wash flag |
| visit_date | TEXT | Date of visit |
| visit_time | TEXT | Time of visit |
| notes | TEXT | Visit notes |

### Author
Muthomi Manasseh

### License
This project was .

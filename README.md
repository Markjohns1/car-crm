# SafiWash CRM
### A Premium, Mobile-First Customer Relationship Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_5-purple.svg)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)](https://www.sqlite.org/)

---

## Project Overview
SafiWash CRM is a high-performance, responsive management portal specifically built for the modern car wash entrepreneur. It transforms messy manual logging into a streamlined, data-driven operation. 

The system solves the critical "Regular Customer" problem—allowing managers to identify their most loyal clients, reward them automatically, and track every shilling of revenue in real-time.

---

## Key Features

### Mobile-First UX (Battle-Tested)
*   **Zero Horizontal Scrolling**: Every page is optimized to lock vertically, ensuring a "native app" feel on smartphones.
*   **Persistent Navigation**: A sticky top header and a robust mobile bottom nav keep essential controls at your fingertips 24/7.
*   **High-Contrast Action Buttons**: Optimized touch targets (stacked buttons) for busy managers on the move.

### Customer & Loyalty Engine
*   **Smart Check-In**: Rapid 3-step visit logging (Customer -> Service -> Payment).
*   **Auto-Loyalty Tracking**: "10 Visits = 1 Free Wash" program is baked in. The system alerts you exactly when a customer is due for a reward.
*   **Full Profiles**: Track visit frequency, total spending, and specific car models for every client.

### Business Intelligence
*   **Revenue Analytics**: Real-time breakdown of Daily, Weekly, and Monthly income.
*   **Top Customer Leaderboard**: Identify your "VIPs" based on total spending.
*   **Service Performance**: See which wash packages (Basic vs. Premium) are driving your growth.

---

## Technical Stack
*   **Backend**: Flask (Python) with high-security session handling.
*   **Database**: SQLite with a relational schema (referential integrity).
*   **Frontend**: Vanilla CSS3 + HTML5 + Bootstrap 5.
*   **Icons**: FontAwesome 6 (Professional Vector Icons).

---

## Documentation for Developers
This codebase is designed for extreme maintainability. It is heavily documented using a block-level methodology:

*   **Logic Blocks**: Every major Python function in app.py features section headers and descriptive docstrings.
*   **UI Blocks**: HTML templates are divided by section comments, making layout changes intuitive.
*   **CSS Fixes**: The stylesheet explicitly labels [MOBILE FIXES], explaining the logic behind critical responsive overrides.

---

## Installation & Setup

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/Markjohns1/car-crm.git
    cd car-crm
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Portal**:
    ```bash
    python app.py
    ```
4.  **Access**: Navigate to http://127.0.0.1:5000

---

## Database Schema

### customers
Stores names, phones, plate numbers, and cumulative metrics (visits, spent, points).

### services
Catalog of wash tiers, prices, and time durations.

### visits
A detailed transaction log linking customers to services with payment methods and timestamps.

---

## Author
**Muthomi Manasseh**
*University Name*
January 2026

"Empowering Kenyan Car Wash Businesses through Data and Design."

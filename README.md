# Daily Collection Loan & Savings Management System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

A comprehensive, feature-complete web application for managing daily loan collections and savings accounts with agent-level multi-tenancy, real-time dashboards, and PDF reporting.

## Project Description

The **Daily Collection Loan & Savings Management System** is a modern, production-ready Flask web application designed to streamline the management of loan portfolios and savings accounts for financial agents and institutions. It provides an intuitive interface for tracking customer profiles, recording transactions, generating daily reports, and exporting data to PDF — all within a secure, multi-agent environment.

## Problem Statement

Traditional loan and savings management often relies on spreadsheets, paper records, or disconnected tools that are error-prone, difficult to audit, and impossible to scale. Agents struggle with:

- Manually tracking loan repayments and savings deposits
- Generating accurate daily and monthly reports
- Managing customer data across multiple agents
- Preventing duplicate or fraudulent customer entries
- Exporting collection data for offline record-keeping

## Solution

This application replaces manual processes with a centralized, web-based platform that:

- Enforces data integrity through server-side validations and CSRF protection
- Provides real-time dashboards with interactive charts for financial insights
- Supports multi-agent workflows with complete data isolation
- Automates PDF report generation for daily collections
- Offers responsive, mobile-friendly UI built on Bootstrap 5

## Features

### Core Functionality
- **Multi-Agent Authentication** — Secure agent registration and login with password hashing
- **Customer Management** — Add, view, block, and delete loan and savings customers
- **Dual Product Types** — Seamless handling of both loan and savings customers from a single profile
- **Transaction Recording** — Log loan collections, withdrawals, savings deposits, and withdrawals with notes
- **Real-Time Dashboards** — Interactive statistics, charts, and recent transaction feeds
- **Advanced Search & Filtering** — Search customers by name, mobile, or Aadhaar; filter by status
- **PDF Export** — Generate and download professional daily collection reports and full transaction history reports
- **Data Validation** — Duplicate mobile/Aadhaar checks, required field enforcement, input sanitization
- **Database Migrations** — Built-in migration support from legacy database schemas
- **Responsive Design** — Fully responsive sidebar layout with mobile breakpoints
- **Flash Messaging** — User-friendly feedback for all actions

### Security
- CSRF protection on all forms via Flask-WTF
- Password hashing with Werkzeug (PBKDF2)
- Session-based authentication with `@login_required` guards
- Server-side input validation and sanitization
- Secure file upload handling with `secure_filename`
- Environment variable configuration for secrets

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 2.0+ |
| **ORM** | SQLAlchemy 2.0+ (via Flask-SQLAlchemy) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | Bootstrap 5.3, Bootstrap Icons |
| **PDF Generation** | ReportLab 4.0+ |
| **Data Processing** | Pandas, NumPy |
| **Security** | Flask-WTF (CSRF), Werkzeug |
| **Template Engine** | Jinja2 |

## Folder Structure

```
daily_c_s/
├── app.py                      # Application entry point and all routes
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── PROJECT_STRUCTURE.md        # Detailed architecture docs
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout with sidebar/navbar
│   ├── login.html              # Agent login page
│   ├── register.html           # Agent registration page
│   ├── dashboard.html          # Unified dashboard overview
│   ├── loan_dashboard.html     # Loan-specific dashboard
│   ├── savings_dashboard.html  # Savings-specific dashboard
│   ├── add_customer.html       # Customer creation form
│   ├── customer_profile.html   # Individual customer detail view
│   ├── reports.html            # Daily datewise reports
│   └── all_report.html         # Full transaction history report
│
├── static/                     # Static assets
│   ├── style.css               # Custom CSS (900+ lines, responsive)
│   └── uploads/                # User-uploaded files and generated PDFs
│
├── instance/                   # Flask instance folder (database lives here)
├── venv/                       # Python virtual environment
└── __pycache__/                # Python bytecode cache
```

## Installation Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/daily_c_s.git
cd daily_c_s
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```
Edit `.env` and set a strong `SECRET_KEY` for production. Adjust `DATABASE_URL` if using PostgreSQL.

### Step 5: Run Database Migrations
```bash
flask db upgrade
```

### Step 6: Start the Application
```bash
python app.py
```
The app will be available at `http://localhost:5000`

## Usage

### Getting Started
1. Open the application in your browser
2. Click **Register** to create a new agent account
3. Log in with your Agent ID and password
4. Start adding customers via the **Add Customer** form
5. Navigate between **Dashboard**, **Loans**, and **Savings** to monitor activity
6. Use **Reports** to view daily collections and export to PDF

### Key Workflows
- **Adding a Loan Customer**: Navigate to Add Customer → Select "Loan" → Fill details → Set initial loan amount and payment → Submit
- **Recording a Collection**: Open a customer profile → Enter amount and note → Submit
- **Generating Reports**: Go to Reports → Select date → View summary → Export PDF
- **Blocking a Customer**: Open customer profile → Click Block to toggle status

## Security Features

| Feature | Implementation |
|---------|---------------|
| **CSRF Protection** | Flask-WTF on all POST forms |
| **Password Hashing** | Werkzeug `generate_password_hash` / `check_password_hash` |
| **Session Security** | Flask session with `SECRET_KEY` from environment |
| **Input Validation** | Regex-based mobile (10-digit) and Aadhaar (12-digit) validation |
| **Duplicate Prevention** | Database-level unique checks on mobile, Aadhaar, and composite keys |
| **Secure File Upload** | `secure_filename`, extension whitelist, size limits |
| **SQL Injection Prevention** | SQLAlchemy ORM parameterized queries throughout |
| **Access Control** | `@login_required` decorator protecting all authenticated routes |

## Screenshots

> *(Replace the placeholders below with actual screenshots of your application)*

| Dashboard | Customer Profile | Reports |
|-----------|-----------------|---------|
| <img src="https://via.placeholder.com/600x350?text=Dashboard" width="300"/> | <img src="https://via.placeholder.com/600x350?text=Customer+Profile" width="300"/> | <img src="https://via.placeholder.com/600x350?text=Daily+Reports" width="300"/> |

| Loan Dashboard | Savings Dashboard | Add Customer |
|----------------|-------------------|--------------|
| <img src="https://via.placeholder.com/600x350?text=Loans" width="300"/> | <img src="https://via.placeholder.com/600x350?text=Savings" width="300"/> | <img src="https://via.placeholder.com/600x350?text=Add+Customer" width="300"/> |

## Future Improvements

- **Role-Based Access Control** — Admin, agent, and viewer roles with granular permissions
- **REST API** — JSON API endpoints for mobile app integration
- **Email Notifications** — Automated reminders for pending payments and due dates
- **Excel Export** — XLSX export alongside existing PDF reports
- **Multi-Language Support** — Internationalization (i18n) for regional languages
- **Audit Logs** — Track all data changes with user, timestamp, and IP
- **Docker Deployment** — Containerized setup with Docker Compose
- **Automated Tests** — pytest suite with CI/CD integration
- **SMS Integration** — Payment reminders via Twilio or similar
- **Data Backup** — Scheduled database backups and restore functionality

## Author

Built with Flask, SQLAlchemy, and Bootstrap.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

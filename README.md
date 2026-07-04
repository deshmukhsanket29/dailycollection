# 🏦 Daily Collection Banking System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1%2B-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red)
![SQLite](https://img.shields.io/badge/SQLite-Ready-teal)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![HTML5](https://img.shields.io/badge/HTML5-Responsive-orange)
![CSS3](https://img.shields.io/badge/CSS3-Modern-blueviolet)

A production-ready Flask web application for managing daily loan collections, savings accounts, and financial agent operations with real-time dashboards, PDF reporting, and secure multi-agent data isolation.

---

## 📖 Project Overview

The **Daily Collection Banking System** is a full-stack web application designed to digitize and streamline the end-to-end workflow of financial agents who manage loan collections and savings accounts. Built with modern web technologies, it replaces manual spreadsheets and paper records with a centralized, secure platform that handles customer onboarding, transaction logging, daily reporting, and performance analytics.

The application supports two distinct customer types — **Loan** and **Savings** — through a unified interface, enabling agents to manage portfolios efficiently. Every customer record is tied to a specific agent, ensuring complete data isolation in multi-agent environments. The system includes real-time dashboards, advanced search, PDF/XLSX export, and responsive design optimized for both desktop and mobile usage.

## ✨ Key Features

- 🔐 **Secure Multi-Agent Authentication** — Registration, login, and session management with password hashing
- 👥 **Comprehensive Customer Management** — Create, view, block, and delete loan and savings customers
- 💰 **Loan & Savings Dual-Mode** — Seamlessly switch between loan collection and savings deposits on a single profile
- 📝 **Transaction Recording** — Log collections, payments, deposits, and withdrawals with timestamps and notes
- 📊 **Real-Time Dashboards** — Interactive statistics and charts for portfolio health and collection trends
- 🔍 **Advanced Search & Filtering** — Search customers by name, mobile, or ID; filter by type, status, and agent
- 📄 **PDF & Excel Reports** — Generate professional daily collection reports and full transaction history exports
- ✅ **Data Integrity & Validation** — Duplicate mobile/Aadhaar checks, required field enforcement, and input sanitization
- 📱 **Responsive Bootstrap UI** — Fully responsive sidebar layout with mobile-first design
- 💾 **Database Migration Support** — Built-in migration support for schema updates

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 3.1+ |
| **ORM** | SQLAlchemy 2.0+ (Flask-SQLAlchemy) |
| **Database** | SQLite (development) / PostgreSQL (production) |
| **Frontend** | Bootstrap 5.3, Bootstrap Icons |
| **PDF Generation** | ReportLab 5.0+ |
| **Data Processing** | Pandas, NumPy |
| **Security** | Flask-WTF (CSRF), Werkzeug |
| **Template Engine** | Jinja2 |

## 🏗 Project Architecture

The application follows the **MVC (Model-View-Controller)** pattern:

- **Models** (`app.py`): SQLAlchemy ORM models for `Agent`, `Customer`, `Loan`, `Savings`, `LoanTransaction`, and `SavingTransaction`
- **Views** (`templates/`): Jinja2 HTML templates with Bootstrap 5 for responsive UI
- **Controllers** (`app.py`): Flask route handlers managing request/response flow, business logic, and data validation

## 📂 Folder Structure

```
daily_c_s/
├── app.py                      # Application entry point and route definitions
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── PROJECT_STRUCTURE.md        # Detailed architecture documentation
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout with sidebar navigation
│   ├── login.html              # Agent login page
│   ├── register.html           # Agent registration page
│   ├── dashboard.html          # Unified dashboard overview
│   ├── loan_dashboard.html     # Loan-specific analytics dashboard
│   ├── savings_dashboard.html  # Savings-specific analytics dashboard
│   ├── add_customer.html       # Customer creation form
│   ├── customer_profile.html   # Individual customer detail view
│   ├── reports.html            # Daily date-wise collection reports
│   ├── all_report.html         # Full transaction history report
│   ├── 404.html                # Custom 404 error page
│   └── 500.html                # Custom 500 error page
│
├── static/                     # Static assets
│   ├── style.css               # Custom CSS (900+ lines, responsive)
│   └── uploads/                # Uploaded photos, PDF, XLSX exports
│
├── instance/                   # Flask instance folder (database lives here)
└── __pycache__/                # Python bytecode cache
```

## 🚀 Installation Guide

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

The application will be available at `http://localhost:5000`

## 📋 Usage

### Getting Started

1. Open the application in your browser
2. Click **Register** to create a new agent account
3. Log in with your Agent ID and password
4. Start adding customers via the **Add Customer** form
5. Navigate between **Dashboard**, **Loan**, and **Savings** to monitor activity
6. Use **Reports** to view daily collections and export to PDF/XLSX

### Key Workflows

- **Adding a Loan Customer**: Navigate to Add Customer → Select "Loan" → Fill customer and loan details → Submit
- **Recording a Collection**: Open a customer profile → Enter amount, transaction type, and note → Submit
- **Generating Reports**: Go to Reports → Select date range → View summary → Export PDF or Excel
- **Blocking a Customer**: Open customer profile → Click Block to toggle Active/Blocked status

## 🗄 Database Design

The database schema is designed around five core entities that map directly to the business domain:

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **Agent** | System user who manages customers | `agent_id`, `name`, `mobile`, `email`, `password_hash` |
| **Customer** | Loan or savings account holder | `full_name`, `mobile`, `aadhaar`, `address`, `customer_type`, `status` |
| **Loan** | Tracks loan amount, paid, and remaining balance | `loan_amount`, `paid_amount`, `remaining_amount`, `status` |
| **Savings** | Tracks daily deposit amounts and total savings | `daily_amount`, `total_saved`, `status` |
| **Transaction** | Individual payment or withdrawal record | `amount`, `transaction_type`, `note`, `date` |

Relationships:
- **Agent** ↔ **Customer** (one-to-many)
- **Customer** ↔ **Loan** / **Savings** (one-to-many)
- **Loan** / **Savings** ↔ **Transaction** (one-to-many)

## 🔐 Authentication

The application uses **session-based authentication** with the following security controls:

- Agents register with a unique `agent_id`, name, mobile, email, and password
- Passwords are hashed using Werkzeug's `generate_password_hash` before storage
- All protected routes use Flask's `@login_required` decorator
- Active sessions are managed via Flask's secure session cookies
- Each agent can only access data associated with their own account

## 🛡 Security Features

| Feature | Implementation |
|---------|---------------|
| **CSRF Protection** | Flask-WTF on all POST forms |
| **Password Hashing** | Werkzeug `generate_password_hash` / `check_password_hash` |
| **Session Security** | Flask session with `SECRET_KEY` from environment variables |
| **Input Validation** | Regex-based mobile (10-digit) and Aadhaar (12-digit) validation |
| **Duplicate Prevention** | Database-level unique checks on mobile, Aadhaar, and composite keys |
| **Secure File Upload** | `secure_filename` with extension whitelist and size limits |
| **SQL Injection Prevention** | SQLAlchemy ORM with parameterized queries |
| **Access Control** | `@login_required` decorator protecting all authenticated routes |

## 📸 Screenshots

> Replace the placeholders below with actual screenshots of your application.

| Dashboard | Customer Profile | Daily Reports |
|-----------|-----------------|---------------|
| `screenshots/dashboard.png` | `screenshots/customer-profile.png` | `screenshots/reports.png` |

| Loan Dashboard | Savings Dashboard | Add Customer |
|----------------|-------------------|--------------|
| `screenshots/loan-dashboard.png` | `screenshots/savings-dashboard.png` | `screenshots/add-customer.png` |

## 🌐 Live Demo

Coming soon.

## 🔭 Future Improvements

- **PostgreSQL Support** — Full production-grade database integration with connection pooling
- **Email Notifications** — Automated reminders for pending payments and due dates
- **SMS Notifications** — Payment reminders and collection alerts via Twilio or similar providers
- **Admin Dashboard** — Super-admin panel for managing multiple agents and viewing system-wide analytics
- **Data Export** — Enhanced CSV, Excel, and JSON export options for all data entities
- **Charts & Analytics** — Advanced visualization trends, agent performance, and customer insights
- **Multi-Agent Support** — Hierarchical agent roles with branch and team management
- **Cloud Backup** — Scheduled automated backups to cloud storage (AWS S3, GCS)

## 🎓 Learning Outcomes

Building and maintaining this project provided hands-on experience with:

- Full-stack web development using Flask and SQLAlchemy
- Database schema design with relational data modeling
- Authentication, authorization, and security best practices
- PDF and Excel report generation with ReportLab and Pandas
- Responsive frontend design with Bootstrap 5 and custom CSS
- Input validation, data sanitization, and CSRF protection
- Git version control and professional documentation

## 👨‍💻 Author

**Sanket Deshmukh**

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

⭐ If you found this project useful, please consider giving it a star on GitHub!

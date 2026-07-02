# Project Structure

Detailed architecture and file reference for the **Daily Collection Loan & Savings Management System**.

## Directory Tree

```
daily_c_s/
│
├── app.py                          # Single-file Flask application (monolithic)
│
├── requirements.txt                # Python package dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
├── README.md                       # Project overview and documentation
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── PROJECT_STRUCTURE.md            # This file
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Master layout (sidebar, navbar, flash messages)
│   ├── login.html                  # Agent login form
│   ├── register.html               # Agent registration form
│   ├── dashboard.html              # Unified dashboard (overview cards + charts)
│   ├── loan_dashboard.html         # Loan-only dashboard
│   ├── savings_dashboard.html      # Savings-only dashboard
│   ├── add_customer.html           # Customer creation form (loan / savings)
│   ├── customer_profile.html       # Customer detail + transaction history
│   ├── reports.html                # Daily datewise report view
│   └── all_report.html             # Combined loan + savings report view
│
├── static/                         # Static assets
│   ├── style.css                   # Custom CSS (sidebar, cards, forms, responsive)
│   └── uploads/                    # User-uploaded photos and generated PDFs
│       ├── *.pdf                   # Generated report files
│       └── *.jpeg / *.jpg / *.png  # Customer profile photos
│
├── instance/                       # Flask instance folder
│   └── database.db                 # SQLite database file (runtime)
│
└── venv/                           # Python virtual environment
    └── ...                         # (excluded from version control)
```

## Application Architecture (`app.py`)

### Configuration
- Flask app initialization with environment-based config
- SQLAlchemy database URI from `DATABASE_URL` env var
- Secret key from `SECRET_KEY` env var
- Upload folder configuration with 16 MB max content length

### Database Models

| Model | Table | Purpose |
|-------|-------|---------|
| `Agent` | `agents` | Registered financial agents (authentication) |
| `Customer` | `customers` | Unified customer record for both loan and savings |
| `Loan` | `loans` | Loan account with amount tracking per customer |
| `Savings` | `savings` | Savings account with daily amount per customer |
| `LoanTransaction` | `loan_transactions` | Individual loan payment/withdrawal records |
| `SavingTransaction` | `saving_transactions` | Individual savings deposit/withdrawal records |

**Key relationships:**
- `Customer` → `Agent` (many-to-one via `agent_id`)
- `Customer` → `Loan` (one-to-one, cascade delete)
- `Customer` → `Savings` (one-to-one, cascade delete)
- `Loan` → `LoanTransaction` (one-to-many, cascade delete)
- `Savings` → `SavingTransaction` (one-to-many, cascade delete)

### Route Groups

| Route Group | Prefix | Lines | Description |
|-------------|--------|-------|-------------|
| Authentication | `/`, `/register`, `/logout` | ~65 | Login, registration, session management |
| Dashboard | `/dashboard`, `/loan_dashboard`, `/savings_dashboard` | ~250 | Overview statistics, charts, recent activity |
| Customer | `/add_customer`, `/customer/<id>`, `/block/<id>`, `/delete/<id>` | ~250 | CRUD + status toggle for customers |
| Transactions | `/add_collection/<id>`, `/add_saving_tx/<id>` | ~110 | Record loan and savings transactions |
| Reports | `/reports`, `/reports/export_pdf`, `/all_report`, `/all_report/export_pdf` | ~280 | Daily and full history reports with PDF export |
| Utilities | `/uploads/<filename>` | ~5 | Serve uploaded files |

### Helper Functions

| Function | Purpose |
|----------|---------|
| `allowed_file(filename)` | Validate image file extensions |
| `validate_mobile(mobile)` | Ensure 10-digit numeric mobile |
| `validate_aadhaar(aadhaar)` | Ensure 12-digit numeric Aadhaar |
| `validate_required(*fields)` | Check for empty or whitespace-only strings |
| `check_duplicate_customer(...)` | Prevent duplicate customer entries |
| `check_duplicate_mobile(...)` | Prevent duplicate mobile numbers per agent |
| `check_duplicate_aadhaar(...)` | Prevent duplicate Aadhaar numbers per agent |
| `get_agent_customers_query()` | Scope queries to logged-in agent |
| `format_currency(amount)` | Format amounts as Indian Rupees (₹) |
| `login_required(f)` | Decorator to enforce authentication |
| `migrate_old_data()` | One-time migration from legacy schema |

### Template Structure

- **`base.html`** — Master layout with sidebar navigation, top navbar, and flash message blocks
- **Auth templates** (`login.html`, `register.html`) — Full-screen auth pages with gradient background
- **Dashboard templates** — Stats cards, Chart.js-ready data arrays, recent transaction tables
- **`add_customer.html`** — Photo upload with preview, dual-mode form for loan/savings
- **`customer_profile.html`** — Profile header with avatar, transaction history tables, action buttons
- **Report templates** — Filterable tables with date selection and PDF export buttons

### Static Assets

- **`style.css`** — 912 lines of custom CSS covering sidebar, cards, forms, tables, auth pages, responsive breakpoints, and utility classes
- **`uploads/`** — Runtime directory for customer photos and generated PDF reports

## Data Flow

```
User Request
    │
    ▼
Flask Route (app.py)
    │
    ├── @login_required → Redirect to / if no session
    │
    ├── Form Submission
    │   ├── Flask-WTF CSRF validation
    │   ├── Server-side input validation
    │   └── Database transaction via SQLAlchemy
    │
    ├── Query
    │   └── SQLAlchemy ORM (scoped to agent_id_pk from session)
    │
    └── Render Template
        ├── Pass data context
        └── Jinja2 renders HTML → Browser
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///database.db` | SQLAlchemy database URI |
| `SECRET_KEY` | Yes | `loan_savings_secret_2024_secure` | Flask session signing key |
| `FLASK_APP` | No | `app.py` | Flask entry point |
| `FLASK_ENV` | No | `production` | Flask environment mode |

## Database Schema

```
agents
├── id (PK)
├── name
├── mobile
├── email
├── agent_id (UNIQUE)
├── password_hash
└── created_at

customers
├── id (PK)
├── agent_id (FK → agents.id)
├── customer_type (loan | savings)
├── full_name
├── father_name
├── mobile (UNIQUE per agent)
├── alternate_mobile
├── aadhaar (UNIQUE per agent)
├── address, city, state, pincode
├── joining_date
├── status (Active | Blocked)
├── notes
├── photo
├── created_at
└── updated_at

loans
├── id (PK)
├── customer_id (FK → customers.id)
├── agent_id (FK → agents.id)
├── loan_amount
├── paid_amount
├── remaining_amount
├── status (Active | Completed)
├── created_at
└── updated_at

savings
├── id (PK)
├── customer_id (FK → customers.id)
├── agent_id (FK → agents.id)
├── daily_amount
├── total_saved
├── status (Active | Completed)
├── created_at
└── updated_at

loan_transactions
├── id (PK)
├── loan_id (FK → loans.id)
├── customer_id (FK → customers.id)
├── agent_id (FK → agents.id)
├── amount
├── transaction_type (credit | debit)
├── note
├── date
└── created_at

saving_transactions
├── id (PK)
├── saving_id (FK → savings.id)
├── customer_id (FK → customers.id)
├── agent_id (FK → agents.id)
├── amount
├── transaction_type (credit | debit)
├── note
├── date
└── created_at
```

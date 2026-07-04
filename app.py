from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy import func, extract, text, inspect, or_
from datetime import datetime, date, timedelta
import os
import re
import time
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ==================== APP CONFIGURATION ====================

app = Flask(__name__)
default_db = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'loan_savings_secret_2024_secure')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['WTF_CSRF_TIME_LIMIT'] = 24 * 60 * 60
app.config['DEBUG'] = False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ==================== MODELS ====================

class Agent(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    agent_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False, index=True)
    customer_type = db.Column(db.String(20), nullable=False, default='loan', index=True)

    full_name = db.Column(db.String(100), nullable=False, index=True)
    father_name = db.Column(db.String(100), nullable=False, default='')
    mobile = db.Column(db.String(20), nullable=False, index=True)
    alternate_mobile = db.Column(db.String(20), nullable=True)
    aadhaar = db.Column(db.String(20), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    joining_date = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), nullable=False, default='Active', index=True)
    notes = db.Column(db.Text, nullable=True)
    photo = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    loans = db.relationship('Loan', backref='customer', lazy=True, cascade='all, delete-orphan')
    savings = db.relationship('Savings', backref='customer', lazy=True, cascade='all, delete-orphan')


class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False, index=True)
    loan_amount = db.Column(db.Integer, nullable=False, default=0)
    paid_amount = db.Column(db.Integer, nullable=False, default=0)
    remaining_amount = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='Active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('LoanTransaction', backref='loan', lazy=True, cascade='all, delete-orphan')


class Savings(db.Model):
    __tablename__ = 'savings'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False, index=True)
    daily_amount = db.Column(db.Integer, nullable=False, default=0)
    total_saved = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='Active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('SavingTransaction', backref='saving', lazy=True, cascade='all, delete-orphan')


class LoanTransaction(db.Model):
    __tablename__ = 'loan_transactions'
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    note = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SavingTransaction(db.Model):
    __tablename__ = 'saving_transactions'
    id = db.Column(db.Integer, primary_key=True)
    saving_id = db.Column(db.Integer, db.ForeignKey('savings.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    note = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== HELPERS ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_mobile(mobile):
    return bool(re.match(r'^[0-9]{10}$', str(mobile)))


def validate_aadhaar(aadhaar):
    return bool(re.match(r'^[0-9]{12}$', str(aadhaar)))


def validate_required(*fields):
    for field in fields:
        if not field or str(field).strip() == '':
            return False
    return True


def check_duplicate_customer(agent_id, full_name, father_name, mobile):
    return Customer.query.filter_by(
        agent_id=agent_id,
        full_name=full_name,
        father_name=father_name,
        mobile=mobile
    ).first() is not None


def check_duplicate_mobile(agent_id, mobile):
    return Customer.query.filter_by(agent_id=agent_id, mobile=mobile).first() is not None


def check_duplicate_aadhaar(agent_id, aadhaar):
    if not aadhaar:
        return False
    return Customer.query.filter_by(agent_id=agent_id, aadhaar=aadhaar).first() is not None


def get_agent_customers_query():
    agent_id_pk = session.get('agent_id_pk')
    if not agent_id_pk:
        return Customer.query.filter(Customer.id == -1)
    return Customer.query.filter_by(agent_id=agent_id_pk)


def format_currency(amount):
    return f"₹{amount:,.0f}"


# ==================== DATABASE MIGRATION ====================

def migrate_old_data():
    with app.app_context():
        try:
            count = Agent.query.count()
            if count > 0:
                return
        except Exception:
            pass

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        if 'agent' not in tables or 'customer' not in tables:
            db.create_all()
            return

        with db.engine.connect() as conn:
            old_agents = conn.execute(text('SELECT * FROM agent')).fetchall()
            for old_agent in old_agents:
                agent = Agent(
                    name=old_agent.name,
                    mobile=old_agent.mobile,
                    email=old_agent.email,
                    agent_id=old_agent.agent_id,
                    password_hash=generate_password_hash(old_agent.password) if old_agent.password else generate_password_hash('default123'),
                    created_at=datetime.utcnow()
                )
                db.session.add(agent)

            db.session.flush()
            first_agent = Agent.query.first()

            old_customers = conn.execute(text('SELECT * FROM customer')).fetchall()
            for old_customer in old_customers:
                created_at_val = old_customer.created_at
                if isinstance(created_at_val, str):
                    try:
                        created_at_val = datetime.strptime(created_at_val, '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        created_at_val = datetime.utcnow()
                elif created_at_val is None:
                    created_at_val = datetime.utcnow()

                customer = Customer(
                    agent_id=first_agent.id if first_agent else 1,
                    customer_type='loan',
                    full_name=old_customer.name,
                    father_name='',
                    mobile=old_customer.mobile,
                    alternate_mobile=None,
                    aadhaar=old_customer.aadhaar or '',
                    address=old_customer.address or '',
                    city=None,
                    state=None,
                    pincode=None,
                    joining_date=datetime.utcnow(),
                    status=old_customer.status or 'Active',
                    notes='',
                    photo=old_customer.photo,
                    created_at=created_at_val,
                    updated_at=datetime.utcnow()
                )
                db.session.add(customer)
                db.session.flush()

                if old_customer.loan_amount and old_customer.loan_amount > 0:
                    loan = Loan(
                        customer_id=customer.id,
                        agent_id=first_agent.id if first_agent else 1,
                        loan_amount=old_customer.loan_amount,
                        paid_amount=old_customer.paid_amount or 0,
                        remaining_amount=old_customer.loan_amount - (old_customer.paid_amount or 0),
                        status='Active',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(loan)
                    db.session.flush()

                    if 'collection' in tables and old_customer.id:
                        old_collections = conn.execute(
                            text('SELECT * FROM collection WHERE customer_id = :cid'),
                            {'cid': old_customer.id}
                        ).fetchall()
                        for old_col in old_collections:
                            amt = old_col.amount if old_col.amount > 0 else abs(old_col.amount)
                            txn_date = old_col.date
                            if isinstance(txn_date, str):
                                try:
                                    txn_date = datetime.strptime(txn_date, '%Y-%m-%d %H:%M:%S')
                                except Exception:
                                    txn_date = datetime.utcnow()
                            elif txn_date is None:
                                txn_date = datetime.utcnow()
                            txn = LoanTransaction(
                                loan_id=loan.id,
                                customer_id=customer.id,
                                agent_id=first_agent.id if first_agent else 1,
                                amount=amt,
                                transaction_type='credit' if old_col.amount > 0 else 'debit',
                                note=old_col.note or 'Migrated transaction',
                                date=txn_date
                            )
                            db.session.add(txn)

            db.session.commit()


# ==================== AUTH DECORATORS ====================

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('agent_id'):
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTH ROUTES ====================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        agent_id = request.form.get("agent_id")
        password = request.form.get("password")
        csrf_token = request.form.get("csrf_token")

        agent = Agent.query.filter_by(agent_id=agent_id).first()

        if agent and check_password_hash(agent.password_hash, password):
            session['agent_name'] = agent.name
            session['agent_id'] = agent.agent_id
            session['agent_id_pk'] = agent.id
            flash(f'Welcome back, {agent.name}!', 'success')
            return redirect(url_for("dashboard"))
        else:
            flash('Invalid Agent ID or Password', 'danger')

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        agent_id = request.form.get("agent_id")
        password = request.form.get("password")

        if not validate_required(name, mobile, email, agent_id, password):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        existing_agent = Agent.query.filter_by(agent_id=agent_id).first()
        if existing_agent:
            flash('Agent ID already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        agent = Agent(
            name=name,
            mobile=mobile,
            email=email,
            agent_id=agent_id,
            password_hash=generate_password_hash(password)
        )

        db.session.add(agent)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    agent_name = session.get('agent_name')
    session.clear()
    if agent_name:
        flash(f'Goodbye, {agent_name}! You have been logged out.', 'info')
    return redirect(url_for("login"))


# ==================== DASHBOARD ROUTES ====================

@app.route("/dashboard")
@login_required
def dashboard():
    agent_id_pk = session.get('agent_id_pk')
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('filter', '').strip()

    customers_query = get_agent_customers_query()
    if search_query:
        customers_query = customers_query.filter(
            or_(
                Customer.full_name.ilike(f'%{search_query}%'),
                Customer.mobile.ilike(f'%{search_query}%'),
                Customer.aadhaar.ilike(f'%{search_query}%')
            )
        )
    if status_filter:
        customers_query = customers_query.filter(Customer.status == status_filter)

    customers = customers_query.all()

    total_customers = len(customers)
    total_loans = db.session.query(func.sum(Loan.loan_amount)).join(Customer).filter(Customer.agent_id == agent_id_pk).scalar() or 0
    total_paid = db.session.query(func.sum(Loan.paid_amount)).join(Customer).filter(Customer.agent_id == agent_id_pk).scalar() or 0
    pending_amount = total_loans - total_paid

    total_collection = db.session.query(func.sum(LoanTransaction.amount)).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.transaction_type == 'credit'
    ).scalar() or 0

    today_start = datetime.combine(datetime.now(), datetime.min.time())
    today_collection = db.session.query(func.sum(LoanTransaction.amount)).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.transaction_type == 'credit',
        LoanTransaction.date >= today_start
    ).scalar() or 0

    recent_payments = LoanTransaction.query.filter_by(agent_id=agent_id_pk).order_by(LoanTransaction.date.desc()).limit(10).all()

    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_data = db.session.query(
        extract('year', LoanTransaction.date).label('year'),
        extract('month', LoanTransaction.date).label('month'),
        func.sum(LoanTransaction.amount).label('total')
    ).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.transaction_type == 'credit',
        LoanTransaction.date >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()

    chart_labels = []
    chart_values = []
    for row in monthly_data:
        chart_labels.append(date(int(row.year), int(row.month), 1).strftime('%b %Y'))
        chart_values.append(float(row.total) if row.total is not None else 0)

    return render_template(
        "dashboard.html",
        customers=customers,
        total_customers=total_customers,
        total_loan_amount=total_loans,
        total_paid_amount=total_paid,
        pending_amount=pending_amount,
        total_collection=total_collection,
        today_collection=today_collection,
        recent_payments=recent_payments,
        chart_labels=chart_labels,
        chart_values=chart_values,
        search_query=search_query,
        status_filter=status_filter,
        agent_name=session.get('agent_name'),
        agent_id=session.get('agent_id')
    )


@app.route("/loan_dashboard")
@login_required
def loan_dashboard():
    agent_id_pk = session.get('agent_id_pk')
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('filter', '').strip()

    loan_query = get_agent_customers_query().filter_by(customer_type='loan').join(Loan)

    if search_query:
        loan_query = loan_query.filter(
            or_(
                Customer.full_name.ilike(f'%{search_query}%'),
                Customer.mobile.ilike(f'%{search_query}%'),
                Customer.aadhaar.ilike(f'%{search_query}%')
            )
        )
    if status_filter:
        if status_filter == 'Pending':
            loan_query = loan_query.filter(Loan.remaining_amount > 0)
        elif status_filter == 'Completed':
            loan_query = loan_query.filter(Loan.remaining_amount <= 0)
        else:
            loan_query = loan_query.filter(Customer.status == status_filter)

    loan_customers = loan_query.all()
    total_loan_customers = len(loan_customers)
    total_loan_amount = db.session.query(func.sum(Loan.loan_amount)).join(Customer).filter(
        Customer.agent_id == agent_id_pk,
        Customer.customer_type == 'loan'
    ).scalar() or 0
    total_collection = db.session.query(func.sum(LoanTransaction.amount)).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.transaction_type == 'credit'
    ).scalar() or 0
    pending_amount = total_loan_amount - (db.session.query(func.sum(Loan.paid_amount)).join(Customer).filter(
        Customer.agent_id == agent_id_pk,
        Customer.customer_type == 'loan'
    ).scalar() or 0)

    today_start = datetime.combine(datetime.now(), datetime.min.time())
    today_collection = db.session.query(func.sum(LoanTransaction.amount)).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.transaction_type == 'credit',
        LoanTransaction.date >= today_start
    ).scalar() or 0

    recent_payments = LoanTransaction.query.filter_by(agent_id=agent_id_pk).order_by(LoanTransaction.date.desc()).limit(10).all()

    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_data = db.session.query(
        extract('year', LoanTransaction.date).label('year'),
        extract('month', LoanTransaction.date).label('month'),
        func.sum(LoanTransaction.amount).label('total')
    ).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.transaction_type == 'credit',
        LoanTransaction.date >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()

    chart_labels = []
    chart_values = []
    for row in monthly_data:
        chart_labels.append(date(int(row.year), int(row.month), 1).strftime('%b %Y'))
        chart_values.append(float(row.total) if row.total is not None else 0)

    paid_vs_pending = {
        'paid': float(db.session.query(func.sum(Loan.paid_amount)).join(Customer).filter(
            Customer.agent_id == agent_id_pk, Customer.customer_type == 'loan'
        ).scalar() or 0),
        'pending': float(pending_amount)
    }

    return render_template(
        "loan_dashboard.html",
        total_loan_customers=total_loan_customers,
        total_loan_amount=total_loan_amount,
        total_collection=total_collection,
        today_collection=today_collection,
        pending_amount=pending_amount,
        recent_payments=recent_payments,
        chart_labels=chart_labels,
        chart_values=chart_values,
        paid_vs_pending=paid_vs_pending,
        search_query=search_query,
        status_filter=status_filter,
        agent_name=session.get('agent_name'),
        agent_id=session.get('agent_id')
    )


@app.route("/savings_dashboard")
@login_required
def savings_dashboard():
    agent_id_pk = session.get('agent_id_pk')
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('filter', '').strip()

    savings_query = get_agent_customers_query().filter_by(customer_type='savings').join(Savings)

    if search_query:
        savings_query = savings_query.filter(
            or_(
                Customer.full_name.ilike(f'%{search_query}%'),
                Customer.mobile.ilike(f'%{search_query}%'),
                Customer.aadhaar.ilike(f'%{search_query}%')
            )
        )
    if status_filter:
        savings_query = savings_query.filter(Customer.status == status_filter)

    savings_members = savings_query.all()
    total_members = len(savings_members)
    total_savings = db.session.query(func.sum(Savings.total_saved)).join(Customer).filter(
        Customer.agent_id == agent_id_pk,
        Customer.customer_type == 'savings'
    ).scalar() or 0

    today_start = datetime.combine(datetime.now(), datetime.min.time())
    today_deposits = db.session.query(func.sum(SavingTransaction.amount)).filter(
        SavingTransaction.agent_id == agent_id_pk,
        SavingTransaction.transaction_type == 'credit',
        SavingTransaction.date >= today_start
    ).scalar() or 0

    today_withdraw = db.session.query(func.sum(SavingTransaction.amount)).filter(
        SavingTransaction.agent_id == agent_id_pk,
        SavingTransaction.transaction_type == 'debit',
        SavingTransaction.date >= today_start
    ).scalar() or 0

    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_deposits = db.session.query(func.sum(SavingTransaction.amount)).filter(
        SavingTransaction.agent_id == agent_id_pk,
        SavingTransaction.transaction_type == 'credit',
        SavingTransaction.date >= current_month_start
    ).scalar() or 0

    recent_transactions = SavingTransaction.query.filter_by(agent_id=agent_id_pk).order_by(SavingTransaction.date.desc()).limit(10).all()

    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_data = db.session.query(
        extract('year', SavingTransaction.date).label('year'),
        extract('month', SavingTransaction.date).label('month'),
        func.sum(SavingTransaction.amount).label('total')
    ).filter(
        SavingTransaction.agent_id == agent_id_pk,
        SavingTransaction.transaction_type == 'credit',
        SavingTransaction.date >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()

    chart_labels = []
    chart_values = []
    for row in monthly_data:
        chart_labels.append(date(int(row.year), int(row.month), 1).strftime('%b %Y'))
        chart_values.append(float(row.total) if row.total is not None else 0)

    return render_template(
        "savings_dashboard.html",
        total_members=total_members,
        total_savings=total_savings,
        today_deposits=today_deposits,
        today_withdraw=abs(today_withdraw) if today_withdraw else 0,
        monthly_deposits=monthly_deposits,
        recent_transactions=recent_transactions,
        chart_labels=chart_labels,
        chart_values=chart_values,
        search_query=search_query,
        status_filter=status_filter,
        agent_name=session.get('agent_name'),
        agent_id=session.get('agent_id')
    )


# ==================== CUSTOMER ROUTES ====================

@app.route("/add_customer", methods=["GET", "POST"])
@login_required
def add_customer():
    if request.method == "POST":
        agent_id_pk = session.get('agent_id_pk')
        customer_type = request.form.get("customer_type", "loan")
        full_name = request.form.get("full_name", "").strip()
        father_name = request.form.get("father_name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        alternate_mobile = request.form.get("alternate_mobile", "").strip()
        aadhaar = request.form.get("aadhaar", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        pincode = request.form.get("pincode", "").strip()
        joining_date_str = request.form.get("joining_date")
        notes = request.form.get("notes", "").strip()

        # Validations
        if not validate_required(full_name, mobile, aadhaar, address, customer_type):
            flash('Full Name, Mobile Number, Aadhaar Number, and Address are required.', 'danger')
            return redirect(url_for('add_customer'))

        if not validate_mobile(mobile):
            flash('Mobile number must be exactly 10 digits.', 'danger')
            return redirect(url_for('add_customer'))

        if not validate_aadhaar(aadhaar):
            flash('Aadhaar number must be exactly 12 digits.', 'danger')
            return redirect(url_for('add_customer'))

        if check_duplicate_mobile(agent_id_pk, mobile):
            flash('A customer with this mobile number already exists.', 'danger')
            return redirect(url_for('add_customer'))

        if check_duplicate_aadhaar(agent_id_pk, aadhaar):
            flash('A customer with this Aadhaar number already exists.', 'danger')
            return redirect(url_for('add_customer'))

        if check_duplicate_customer(agent_id_pk, full_name, father_name, mobile):
            flash('A customer with this Name, Father Name, and Mobile already exists.', 'danger')
            return redirect(url_for('add_customer'))

        # Parse joining date
        joining_date = datetime.utcnow()
        if joining_date_str:
            try:
                joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d')
            except ValueError:
                pass

        # Photo upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = int(time.time())
                ext = filename.rsplit('.', 1)[1].lower()
                photo_filename = f"{timestamp}_{full_name.replace(' ', '_')}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Create customer
        customer = Customer(
            agent_id=agent_id_pk,
            customer_type=customer_type,
            full_name=full_name,
            father_name=father_name,
            mobile=mobile,
            alternate_mobile=alternate_mobile or None,
            aadhaar=aadhaar,
            address=address,
            city=city or None,
            state=state or None,
            pincode=pincode or None,
            joining_date=joining_date,
            status='Active',
            notes=notes or None,
            photo=photo_filename
        )
        db.session.add(customer)
        db.session.flush()

        # Create type-specific record
        if customer_type == 'loan':
            loan_amount = int(request.form.get("loan_amount") or 0)
            initial_payment = int(request.form.get("initial_payment") or 0)

            loan = Loan(
                customer_id=customer.id,
                agent_id=agent_id_pk,
                loan_amount=loan_amount,
                paid_amount=initial_payment,
                remaining_amount=loan_amount - initial_payment,
                status='Active' if loan_amount > 0 else 'Completed',
                created_at=datetime.utcnow()
            )
            db.session.add(loan)
            db.session.flush()

            if initial_payment > 0:
                txn = LoanTransaction(
                    loan_id=loan.id,
                    customer_id=customer.id,
                    agent_id=agent_id_pk,
                    amount=initial_payment,
                    transaction_type='credit',
                    note='Initial payment',
                    date=datetime.utcnow()
                )
                db.session.add(txn)

        elif customer_type == 'savings':
            daily_amount = int(request.form.get("daily_amount") or 0)
            initial_deposit = int(request.form.get("initial_deposit") or 0)

            savings = Savings(
                customer_id=customer.id,
                agent_id=agent_id_pk,
                daily_amount=daily_amount,
                total_saved=initial_deposit,
                status='Active',
                created_at=datetime.utcnow()
            )
            db.session.add(savings)
            db.session.flush()

            if initial_deposit > 0:
                txn = SavingTransaction(
                    saving_id=savings.id,
                    customer_id=customer.id,
                    agent_id=agent_id_pk,
                    amount=initial_deposit,
                    transaction_type='credit',
                    note='Initial deposit',
                    date=datetime.utcnow()
                )
                db.session.add(txn)

        db.session.commit()
        flash(f'{customer_type.title()} member {full_name} added successfully!', 'success')
        return redirect(url_for("dashboard"))

    return render_template("add_customer.html")


@app.route("/customer/<int:id>")
@login_required
def customer_profile(id):
    agent_id_pk = session.get('agent_id_pk')
    customer = Customer.query.filter_by(id=id, agent_id=agent_id_pk).first_or_404()

    loan_transactions = []
    saving_transactions = []
    loan_info = None
    savings_info = None

    if customer.customer_type == 'loan':
        loan_info = Loan.query.filter_by(customer_id=customer.id).first()
        if loan_info:
            loan_transactions = LoanTransaction.query.filter_by(loan_id=loan_info.id).order_by(LoanTransaction.date.desc()).all()

    elif customer.customer_type == 'savings':
        savings_info = Savings.query.filter_by(customer_id=customer.id).first()
        if savings_info:
            saving_transactions = SavingTransaction.query.filter_by(saving_id=savings_info.id).order_by(SavingTransaction.date.desc()).all()

            customer.total_deposits = SavingTransaction.query.filter(
                SavingTransaction.saving_id == savings_info.id,
                SavingTransaction.transaction_type == 'credit'
            ).with_entities(func.sum(SavingTransaction.amount)).scalar() or 0

            customer.total_withdraw = abs(SavingTransaction.query.filter(
                SavingTransaction.saving_id == savings_info.id,
                SavingTransaction.transaction_type == 'debit'
            ).with_entities(func.sum(SavingTransaction.amount)).scalar() or 0)

            today_start = datetime.combine(datetime.now(), datetime.min.time())
            customer.today_deposit = SavingTransaction.query.filter(
                SavingTransaction.saving_id == savings_info.id,
                SavingTransaction.transaction_type == 'credit',
                SavingTransaction.date >= today_start
            ).with_entities(func.sum(SavingTransaction.amount)).scalar() or 0

    return render_template(
        "customer_profile.html",
        customer=customer,
        loan_info=loan_info,
        savings_info=savings_info,
        loan_transactions=loan_transactions,
        saving_transactions=saving_transactions
    )


# ==================== TRANSACTION ROUTES ====================

@app.route("/add_collection/<int:id>", methods=["POST"])
@login_required
def add_collection(id):
    agent_id_pk = session.get('agent_id_pk')
    customer = Customer.query.filter_by(id=id, agent_id=agent_id_pk).first_or_404()

    if customer.customer_type != 'loan':
        flash('This customer is not a loan customer.', 'warning')
        return redirect(url_for('customer_profile', id=id))

    loan = Loan.query.filter_by(customer_id=customer.id).first()
    if not loan:
        flash('No loan record found.', 'warning')
        return redirect(url_for('customer_profile', id=id))

    amount = int(request.form.get("amount") or 0)
    t_type = request.form.get("transaction_type")
    note = request.form.get("note", "")

    if amount <= 0:
        flash('Please enter a valid amount.', 'danger')
        return redirect(url_for('customer_profile', id=id))

    if t_type == "debit":
        amount = -amount

    txn = LoanTransaction(
        loan_id=loan.id,
        customer_id=customer.id,
        agent_id=agent_id_pk,
        amount=amount,
        transaction_type=t_type,
        note=note,
        date=datetime.utcnow()
    )
    db.session.add(txn)

    loan.paid_amount = (loan.paid_amount or 0) + amount
    loan.remaining_amount = (loan.loan_amount or 0) - (loan.paid_amount or 0)

    if loan.remaining_amount <= 0:
        loan.remaining_amount = 0
        loan.status = 'Completed'

    db.session.commit()

    if t_type == 'credit':
        flash(f'Payment of {format_currency(abs(amount))} added successfully!', 'success')
    else:
        flash(f'Withdrawal of {format_currency(abs(amount))} processed successfully!', 'success')

    return redirect(url_for("customer_profile", id=id))


@app.route("/add_saving_tx/<int:id>", methods=["POST"])
@login_required
def add_saving_tx(id):
    agent_id_pk = session.get('agent_id_pk')
    customer = Customer.query.filter_by(id=id, agent_id=agent_id_pk).first_or_404()

    if customer.customer_type != 'savings':
        flash('This customer is not a savings member.', 'warning')
        return redirect(url_for('customer_profile', id=id))

    savings = Savings.query.filter_by(customer_id=customer.id).first()
    if not savings:
        flash('No savings record found.', 'warning')
        return redirect(url_for('customer_profile', id=id))

    amount = int(request.form.get("amount") or 0)
    t_type = request.form.get("transaction_type")
    note = request.form.get("note", "")

    if amount <= 0:
        flash('Please enter a valid amount.', 'danger')
        return redirect(url_for('customer_profile', id=id))

    if t_type == "debit":
        current_balance = savings.total_saved or 0
        if amount > current_balance:
            flash(f'Insufficient balance. Current balance: {format_currency(current_balance)}', 'danger')
            return redirect(url_for('customer_profile', id=id))
        amount = -amount

    txn = SavingTransaction(
        saving_id=savings.id,
        customer_id=customer.id,
        agent_id=agent_id_pk,
        amount=amount,
        transaction_type=t_type,
        note=note,
        date=datetime.utcnow()
    )
    db.session.add(txn)

    savings.total_saved = (savings.total_saved or 0) + amount
    db.session.commit()

    if t_type == 'credit':
        flash(f'Deposit of {format_currency(abs(amount))} added successfully!', 'success')
    else:
        flash(f'Withdrawal of {format_currency(abs(amount))} processed successfully!', 'success')

    return redirect(url_for("customer_profile", id=id))


# ==================== CUSTOMER MANAGEMENT ====================

@app.route("/block/<int:id>")
@login_required
def block_customer(id):
    agent_id_pk = session.get('agent_id_pk')
    customer = Customer.query.filter_by(id=id, agent_id=agent_id_pk).first_or_404()

    if customer.status == "Active":
        customer.status = "Blocked"
        flash(f'Customer {customer.full_name} has been blocked.', 'warning')
    else:
        customer.status = "Active"
        flash(f'Customer {customer.full_name} has been unblocked.', 'success')

    db.session.commit()
    return redirect(url_for("customer_profile", id=id))


@app.route("/delete/<int:id>")
@login_required
def delete_customer(id):
    agent_id_pk = session.get('agent_id_pk')
    customer = Customer.query.filter_by(id=id, agent_id=agent_id_pk).first_or_404()
    customer_name = customer.full_name

    if customer.photo:
        try:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], customer.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except Exception:
            pass

    db.session.delete(customer)
    db.session.commit()

    flash(f'Customer {customer_name} has been deleted.', 'success')
    return redirect(url_for("dashboard"))


# ==================== REPORTS ROUTES ====================

@app.route("/reports")
@login_required
def reports():
    agent_id_pk = session.get('agent_id_pk')
    mode = request.args.get('mode', '')
    
    if mode == 'datewise':
        report_date_str = request.args.get('report_date', '')
        if not report_date_str:
            report_date = datetime.now().date()
        else:
            report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()

        day_start = datetime.combine(report_date, datetime.min.time())
        day_end = datetime.combine(report_date, datetime.max.time())

        loan_query = db.session.query(
            LoanTransaction, Loan, Customer
        ).join(Loan, LoanTransaction.loan_id == Loan.id).join(
            Customer, LoanTransaction.customer_id == Customer.id
        ).filter(
            LoanTransaction.agent_id == agent_id_pk,
            LoanTransaction.date >= day_start,
            LoanTransaction.date <= day_end
        ).order_by(LoanTransaction.date.desc()).all()

        savings_query = db.session.query(
            SavingTransaction, Savings, Customer
        ).join(Savings, SavingTransaction.saving_id == Savings.id).join(
            Customer, SavingTransaction.customer_id == Customer.id
        ).filter(
            SavingTransaction.agent_id == agent_id_pk,
            SavingTransaction.date >= day_start,
            SavingTransaction.date <= day_end
        ).order_by(SavingTransaction.date.desc()).all()

        loan_rows = []
        total_loan_collection = 0
        for tx, loan, customer in loan_query:
            amount = abs(tx.amount) if tx.amount else 0
            total_loan_collection += amount
            loan_rows.append({
                'customer_name': customer.full_name,
                'amount': amount,
                'time': tx.date.strftime('%H:%M') if tx.date else 'N/A'
            })

        savings_rows = []
        total_savings_collection = 0
        for tx, savings, customer in savings_query:
            if tx.transaction_type == 'credit':
                amount = abs(tx.amount) if tx.amount else 0
                total_savings_collection += amount
            else:
                amount = 0
            savings_rows.append({
                'member_name': customer.full_name,
                'amount': amount,
                'time': tx.date.strftime('%H:%M') if tx.date else 'N/A'
            })

        total_collection = total_loan_collection + total_savings_collection

        total_loan_customers = db.session.query(func.count(func.distinct(Customer.id))).filter(
            Customer.agent_id == agent_id_pk, Customer.customer_type == 'loan'
        ).scalar() or 0

        total_savings_members = db.session.query(func.count(func.distinct(Customer.id))).filter(
            Customer.agent_id == agent_id_pk, Customer.customer_type == 'savings'
        ).scalar() or 0

        return render_template(
            'reports.html',
            mode='datewise',
            report_date=report_date,
            loan_rows=loan_rows,
            savings_rows=savings_rows,
            total_loan_collection=total_loan_collection,
            total_savings_collection=total_savings_collection,
            total_collection=total_collection,
            total_loan_customers=total_loan_customers,
            total_savings_members=total_savings_members,
            selected_date=report_date.strftime('%Y-%m-%d'),
            agent_name=session.get('agent_name')
        )
    else:
        return render_template('reports.html', mode='', agent_name=session.get('agent_name'))


@app.route("/reports/export_pdf")
@login_required
def export_pdf():
    agent_id_pk = session.get('agent_id_pk')
    report_date_str = request.args.get('report_date', '')

    if not report_date_str:
        report_date = datetime.now().date()
    else:
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()

    day_start = datetime.combine(report_date, datetime.min.time())
    day_end = datetime.combine(report_date, datetime.max.time())

    loan_query = db.session.query(
        LoanTransaction, Loan, Customer
    ).join(Loan, LoanTransaction.loan_id == Loan.id).join(
        Customer, LoanTransaction.customer_id == Customer.id
    ).filter(
        LoanTransaction.agent_id == agent_id_pk,
        LoanTransaction.date >= day_start,
        LoanTransaction.date <= day_end
    ).order_by(LoanTransaction.date.desc()).all()

    savings_query = db.session.query(
        SavingTransaction, Savings, Customer
    ).join(Savings, SavingTransaction.saving_id == Savings.id).join(
        Customer, SavingTransaction.customer_id == Customer.id
    ).filter(
        SavingTransaction.agent_id == agent_id_pk,
        SavingTransaction.date >= day_start,
        SavingTransaction.date <= day_end
    ).order_by(SavingTransaction.date.desc()).all()

    loan_rows = []
    total_loan_collection = 0
    for tx, loan, customer in loan_query:
        amount = abs(tx.amount) if tx.amount else 0
        total_loan_collection += amount
        loan_rows.append({
            'customer_name': customer.full_name,
            'amount': amount
        })

    savings_rows = []
    total_savings_collection = 0
    for tx, savings, customer in savings_query:
        if tx.transaction_type == 'credit':
            amount = abs(tx.amount) if tx.amount else 0
            total_savings_collection += amount
        else:
            amount = 0
        savings_rows.append({
            'member_name': customer.full_name,
            'amount': amount
        })

    total_collection = total_loan_collection + total_savings_collection

    total_loan_customers = db.session.query(func.count(func.distinct(Customer.id))).filter(
        Customer.agent_id == agent_id_pk, Customer.customer_type == 'loan'
    ).scalar() or 0

    total_savings_members = db.session.query(func.count(func.distinct(Customer.id))).filter(
        Customer.agent_id == agent_id_pk, Customer.customer_type == 'savings'
    ).scalar() or 0

    filename = f"report_{report_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Daily Collection Loan & Savings Management System", styles['Title']))
    elements.append(Paragraph(f"Selected Date: {report_date.strftime('%d %b %Y')}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph("Loan Collection", styles['Heading2']))
    elements.append(Paragraph(f"Rs.{total_loan_collection:,.0f}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph("Savings Collection", styles['Heading2']))
    elements.append(Paragraph(f"Rs.{total_savings_collection:,.0f}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph("Total Collection", styles['Heading2']))
    elements.append(Paragraph(f"Rs.{total_collection:,.0f}", styles['Normal']))
    elements.append(Paragraph(f"Total Loan Customers: {total_loan_customers}", styles['Normal']))
    elements.append(Paragraph(f"Total Savings Members: {total_savings_members}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    if loan_rows:
        elements.append(Paragraph("Loan Collection Table", styles['Heading2']))
        loan_data = [['Customer Name', 'Amount']]
        for r in loan_rows:
            loan_data.append([r['customer_name'], f"Rs.{r['amount']:,.0f}"])
        loan_table = Table(loan_data, hAlign='LEFT')
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fc')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fc'), colors.white]),
        ]))
        elements.append(loan_table)
        elements.append(Paragraph("<br/>", styles['Normal']))

    if savings_rows:
        elements.append(Paragraph("Savings Collection Table", styles['Heading2']))
        sav_data = [['Member Name', 'Amount']]
        for r in savings_rows:
            sav_data.append([r['member_name'], f"Rs.{r['amount']:,.0f}"])
        sav_table = Table(sav_data, hAlign='LEFT')
        sav_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1cc88a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fc')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fc'), colors.white]),
        ]))
        elements.append(sav_table)
        elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", styles['Normal']))

    doc.build(elements)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/all_report')
@login_required
def all_report():
    agent_id_pk = session.get('agent_id_pk')

    loan_query = db.session.query(
        LoanTransaction, Loan, Customer
    ).join(Loan, LoanTransaction.loan_id == Loan.id).join(
        Customer, LoanTransaction.customer_id == Customer.id
    ).filter(
        LoanTransaction.agent_id == agent_id_pk
    ).order_by(LoanTransaction.date.desc()).all()

    savings_query = db.session.query(
        SavingTransaction, Savings, Customer
    ).join(Savings, SavingTransaction.saving_id == Savings.id).join(
        Customer, SavingTransaction.customer_id == Customer.id
    ).filter(
        SavingTransaction.agent_id == agent_id_pk
    ).order_by(SavingTransaction.date.desc()).all()

    combined_rows = []
    total_loan_collection = 0
    total_savings_collection = 0
    total_transactions = 0

    for tx, loan, customer in loan_query:
        amount = abs(tx.amount) if tx.amount else 0
        total_loan_collection += amount
        total_transactions += 1
        combined_rows.append({
            'date': tx.date,
            'customer_name': customer.full_name,
            'type': 'Loan',
            'amount': amount,
            'time': tx.date.strftime('%H:%M') if tx.date else 'N/A'
        })

    for tx, savings, customer in savings_query:
        if tx.transaction_type == 'credit':
            amount = abs(tx.amount) if tx.amount else 0
            total_savings_collection += amount
        else:
            amount = 0
        total_transactions += 1
        combined_rows.append({
            'date': tx.date,
            'customer_name': customer.full_name,
            'type': 'Savings',
            'amount': amount,
            'time': tx.date.strftime('%H:%M') if tx.date else 'N/A'
        })

    combined_rows.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
    grand_total = total_loan_collection + total_savings_collection

    return render_template(
        'all_report.html',
        combined_rows=combined_rows,
        total_loan_collection=total_loan_collection,
        total_savings_collection=total_savings_collection,
        grand_total=grand_total,
        total_transactions=total_transactions,
        agent_name=session.get('agent_name')
    )


@app.route('/all_report/export_pdf')
@login_required
def all_report_export_pdf():
    agent_id_pk = session.get('agent_id_pk')

    loan_query = db.session.query(
        LoanTransaction, Loan, Customer
    ).join(Loan, LoanTransaction.loan_id == Loan.id).join(
        Customer, LoanTransaction.customer_id == Customer.id
    ).filter(
        LoanTransaction.agent_id == agent_id_pk
    ).order_by(LoanTransaction.date.desc()).all()

    savings_query = db.session.query(
        SavingTransaction, Savings, Customer
    ).join(Savings, SavingTransaction.saving_id == Savings.id).join(
        Customer, SavingTransaction.customer_id == Customer.id
    ).filter(
        SavingTransaction.agent_id == agent_id_pk
    ).order_by(SavingTransaction.date.desc()).all()

    combined_rows = []
    total_loan_collection = 0
    total_savings_collection = 0
    total_transactions = 0

    for tx, loan, customer in loan_query:
        amount = abs(tx.amount) if tx.amount else 0
        total_loan_collection += amount
        total_transactions += 1
        combined_rows.append({
            'date': tx.date,
            'customer_name': customer.full_name,
            'type': 'Loan',
            'amount': amount,
            'time': tx.date.strftime('%H:%M') if tx.date else 'N/A'
        })

    for tx, savings, customer in savings_query:
        if tx.transaction_type == 'credit':
            amount = abs(tx.amount) if tx.amount else 0
            total_savings_collection += amount
        else:
            amount = 0
        total_transactions += 1
        combined_rows.append({
            'date': tx.date,
            'customer_name': customer.full_name,
            'type': 'Savings',
            'amount': amount,
            'time': tx.date.strftime('%H:%M') if tx.date else 'N/A'
        })

    combined_rows.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
    grand_total = total_loan_collection + total_savings_collection

    filename = f"all_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Daily Collection Loan & Savings Management System", styles['Title']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph("Total Loan Collection", styles['Heading2']))
    elements.append(Paragraph(f"Rs.{total_loan_collection:,.0f}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph("Total Savings Collection", styles['Heading2']))
    elements.append(Paragraph(f"Rs.{total_savings_collection:,.0f}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    elements.append(Paragraph("Grand Total Collection", styles['Heading2']))
    elements.append(Paragraph(f"Rs.{grand_total:,.0f}", styles['Normal']))
    elements.append(Paragraph(f"Total Transactions: {total_transactions}", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    if combined_rows:
        elements.append(Paragraph("All Transactions", styles['Heading2']))
        table_data = [['Date', 'Customer / Member Name', 'Type', 'Amount', 'Time']]
        for r in combined_rows:
            table_data.append([
                r['date'].strftime('%d %b %Y') if r['date'] else 'N/A',
                r['customer_name'],
                r['type'],
                f"Rs.{r['amount']:,.0f}",
                r['time']
            ])
        table = Table(table_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fc')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fc'), colors.white]),
        ]))
        elements.append(table)

    doc.build(elements)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# ==================== UTILITY ROUTES ====================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    flash('Page not found.', 'danger')
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('An internal error occurred. Please try again.', 'danger')
    return render_template('500.html'), 500


# ==================== RUN APP ====================

with app.app_context():
    db.create_all()
    migrate_old_data()

if __name__ == "__main__":
    app.run()

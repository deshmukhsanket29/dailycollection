from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "daily_collection_secret_2024"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ==================== HELPER FUNCTIONS ====================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== MODELS ====================

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    agent_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255))
    aadhaar = db.Column(db.String(20))
    loan_amount = db.Column(db.Integer, default=0)
    paid_amount = db.Column(db.Integer, default=0)
    photo = db.Column(db.String(255))
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10))  # credit or debit
    note = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== AUTH ROUTES ====================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        agent_id = request.form.get("agent_id")
        password = request.form.get("password")
        
        agent = Agent.query.filter_by(
            agent_id=agent_id,
            password=password
        ).first()

        if agent:
            session['agent_name'] = agent.name
            session['agent_id'] = agent.agent_id
            session['agent_id_pk'] = agent.id
            flash('Welcome back, ' + agent.name + '!', 'success')
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
        
        # Check if agent_id already exists
        existing_agent = Agent.query.filter_by(agent_id=agent_id).first()
        if existing_agent:
            flash('Agent ID already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        agent = Agent(
            name=name,
            mobile=mobile,
            email=email,
            agent_id=agent_id,
            password=password
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


# ==================== DASHBOARD ROUTE ====================

@app.route("/dashboard")
def dashboard():
    # Check if user is logged in
    if not session.get('agent_id'):
        flash('Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    
    # Get statistics
    total_customers = Customer.query.count()
    
    # Total collection (sum of all positive amounts)
    total_collection = db.session.query(
        func.sum(Collection.amount)
    ).filter(Collection.amount > 0).scalar() or 0
    
    # Today's collection
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_collection = db.session.query(
        func.sum(Collection.amount)
    ).filter(
        Collection.date >= today_start,
        Collection.amount > 0
    ).scalar() or 0
    
    # Pending amount (sum of all loan amounts - paid amounts) for customers with loan only
    total_loan = db.session.query(func.sum(Customer.loan_amount)).filter(Customer.loan_amount > 0).scalar() or 0
    total_paid = db.session.query(func.sum(Customer.paid_amount)).filter(Customer.loan_amount > 0).scalar() or 0
    pending_amount = total_loan - total_paid
    
    # Get all customers
    customers = Customer.query.all()
    
    # Get recent payments (last 10)
    recent_payments = Collection.query.order_by(Collection.date.desc()).limit(10).all()
    
    return render_template(
        "dashboard.html",
        customers=customers,
        total_customers=total_customers,
        total_collection=total_collection,
        today_collection=today_collection,
        pending_amount=pending_amount,
        recent_payments=recent_payments,
        agent_name=session.get('agent_name'),
        agent_id=session.get('agent_id')
    )


# ==================== CUSTOMER ROUTES ====================

@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if not session.get('agent_id'):
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == "POST":
        name = request.form.get("name")
        mobile = request.form.get("mobile")
        address = request.form.get("address")
        has_loan = request.form.get("has_loan")
        
        # If checkbox is checked, use the loan amount; otherwise set to 0
        if has_loan:
            loan_amount = int(request.form.get("loan_amount") or 0)
        else:
            loan_amount = 0
            
        initial_payment = int(request.form.get("initial_payment") or 0)
        
        # Handle photo upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                import time
                timestamp = int(time.time())
                ext = filename.rsplit('.', 1)[1].lower()
                photo_filename = f"{timestamp}_{name.replace(' ', '_')}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        customer = Customer(
            name=name,
            mobile=mobile,
            address=address,
            loan_amount=loan_amount,
            paid_amount=initial_payment,
            photo=photo_filename,
            status="Active"
        )
        
        db.session.add(customer)
        db.session.commit()
        
        # If there's initial payment, create a collection record
        if initial_payment > 0:
            collection = Collection(
                customer_id=customer.id,
                amount=initial_payment,
                transaction_type="credit",
                note="Initial payment"
            )
            db.session.add(collection)
            db.session.commit()
        
        flash(f'Customer {name} added successfully!', 'success')
        return redirect(url_for("dashboard"))
    
    return render_template("add_customer.html")


@app.route("/customer/<int:id>")
def customer_profile(id):
    if not session.get('agent_id'):
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
    
    customer = Customer.query.get_or_404(id)
    payments = Collection.query.filter_by(customer_id=id).order_by(Collection.date.desc()).all()
    
    return render_template(
        "customer_profile.html",
        customer=customer,
        payments=payments
    )


# ==================== TRANSACTION ROUTES ====================

@app.route("/add_collection/<int:id>", methods=["POST"])
def add_collection(id):
    if not session.get('agent_id'):
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
    
    customer = Customer.query.get_or_404(id)
    
    # Check if customer has a loan
    if customer.loan_amount <= 0:
        flash('This customer has no loan.', 'warning')
        return redirect(url_for('customer_profile', id=id))
    
    amount = int(request.form.get("amount") or 0)
    t_type = request.form.get("transaction_type")
    note = request.form.get("note", "")
    
    if amount <= 0:
        flash('Please enter a valid amount.', 'danger')
        return redirect(url_for('customer_profile', id=id))
    
    # Convert to negative for debit
    if t_type == "debit":
        amount = -amount
    
    # Create collection record
    payment = Collection(
        customer_id=id,
        amount=amount,
        transaction_type=t_type,
        note=note
    )
    
    db.session.add(payment)
    
    # Update customer's paid amount
    customer.paid_amount = (customer.paid_amount or 0) + amount
    
    db.session.commit()
    
    if t_type == "credit":
        flash(f'Payment of ₹{amount} added successfully!', 'success')
    else:
        flash(f'Withdrawal of ₹{abs(amount)} processed successfully!', 'success')
    
    return redirect(url_for("customer_profile", id=id))


# ==================== CUSTOMER MANAGEMENT ROUTES ====================

@app.route("/block/<int:id>")
def block_customer(id):
    if not session.get('agent_id'):
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
    
    customer = Customer.query.get_or_404(id)
    
    if customer.status == "Active":
        customer.status = "Blocked"
        flash(f'Customer {customer.name} has been blocked.', 'warning')
    else:
        customer.status = "Active"
        flash(f'Customer {customer.name} has been unblocked.', 'success')
    
    db.session.commit()
    return redirect(url_for("customer_profile", id=id))


@app.route("/delete/<int:id>")
def delete_customer(id):
    if not session.get('agent_id'):
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('login'))
    
    customer = Customer.query.get_or_404(id)
    customer_name = customer.name
    
    # Delete associated collections first
    Collection.query.filter_by(customer_id=id).delete()
    
    # Delete customer photo if exists
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


# ==================== UTILITY ROUTES ====================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    flash('Page not found.', 'danger')
    return redirect(url_for('dashboard'))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('An internal error occurred. Please try again.', 'danger')
    return redirect(url_for('dashboard'))


# ==================== RUN APP ====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)

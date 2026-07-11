# 🏦 Daily Collection & Savings Management System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-black)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![SQLite](https://img.shields.io/badge/SQLite-Database-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/License-MIT-blue)

A Flask-based web application that helps small finance agents manage daily loan collections and savings records digitally. The system provides a simple way to manage customers, record transactions, monitor balances, and generate PDF reports from a single dashboard.


---

# 📖 Project Overview

Many finance agents in villages and small towns still maintain customer records in notebooks. Managing daily collections, savings, customer details, and transaction history manually is time-consuming and can lead to mistakes.

To solve this problem, I built this web application using **Flask**, **SQLAlchemy**, and **Bootstrap**. It allows agents to manage customers, record loan collections and savings transactions, monitor balances, and generate reports through a simple and user-friendly interface.

---

# ✨ Features

## 🔐 Authentication

- Agent Registration
- Secure Login
- Logout
- Session-based Authentication
- Password Hashing

---

## 👥 Customer Management

- Add Loan Customers
- Add Savings Members
- Customer Profile
- Customer Photo Upload
- Block / Unblock Customers
- Delete Customers

---

## 💰 Loan & Savings Management

### Loan

- Create Loan Records
- Record Daily Loan Collections
- Track Paid Amount
- Track Remaining Amount

### Savings

- Deposit Money
- Withdraw Money
- Track Current Balance
- Running Balance Validation

---

## 📊 Dashboard

- Dashboard Overview
- Loan Dashboard
- Savings Dashboard
- Monthly Collection Charts
- Monthly Savings Charts
- Recent Transactions
- Collection Summary

---

## 🔍 Search & Filters

- Search by Name
- Search by Mobile Number
- Search by Aadhaar Number
- Filter Active Customers
- Filter Blocked Customers
- Filter Pending Loans
- Filter Completed Loans

---

## 📄 Reports

- Date-wise Collection Report
- Complete Transaction History
- Export Reports as PDF

---

# 🛠 Tech Stack

### Backend

- Python
- Flask
- SQLAlchemy

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- Jinja2

### Database

- SQLite

### Libraries

- Flask-WTF
- Werkzeug
- ReportLab
- Chart.js

---

# 🌐 Live Demo

### Project URL

https://dailycollection.onrender.com

> **Note:** The application is hosted on Render's free plan. The first request may take around **30–60 seconds** if the server is inactive.

---

# 🚀 How to Test the Application

### Step 1

Open the Live Demo.

### Step 2

Click **Create Account** and register a new Agent account.

### Step 3

Login using your **Agent ID** and **Password**.

### Step 4

Click **Add Customer** and create a Loan Customer or Savings Member.

### Step 5

Visit the Dashboard to view:

- Customer Statistics
- Collection Summary
- Monthly Charts

### Step 6

Open any Customer Profile and record:

- Loan Collection
- Savings Deposit
- Savings Withdrawal

### Step 7

Visit the **Reports** section to:

- Generate Date-wise Reports
- View Complete Transaction History
- Export Reports as PDF

---

# 🔒 Security Features

- Password Hashing
- Session Authentication
- CSRF Protection
- Protected Routes
- Secure File Upload
- Mobile Number Validation
- Aadhaar Validation
- Duplicate Customer Validation
- SQLAlchemy ORM Protection

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/deshmukhsanket29/dailycollection
```

Move into the project

```bash
cd daily_collection_system
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run the Application

```bash
python app.py
```

---

# 🔮 Future Improvements

- Excel Report Export
- CSV Export
- Email Notifications
- SMS Notifications
- Admin Dashboard
- Role-based Access Control
- PostgreSQL Support

---

# 👨‍💻 About the Author

## Sanket Deshmukh

**B.Tech (Computer Science) | 2nd Year Student**  
**Specialization: Data Science**

I believe that building real-world projects is one of the best ways to learn software development. Although my specialization is in Data Science, I also focus on strengthening my fundamentals in programming and web development by creating practical applications.

Whenever I come across a real-life problem, I try to solve it through software. This project was inspired by the challenges faced by local finance agents who still maintain daily collection records manually in notebooks. Building this application helped me improve my understanding of Flask, database design, authentication, reporting, and full-stack development while working on a practical use case.

### Connect with Me

**LinkedIn**

https://www.linkedin.com/in/sanket-deshmukh-521433323/

**GitHub**

https://github.com/deshmukhsanket29

---

⭐ If you found this project useful, consider giving it a **Star** on GitHub.
# Contributing

Thank you for your interest in contributing to the **Daily Collection Loan & Savings Management System**! This document provides guidelines and steps for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with the following information:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots or error logs (if applicable)
- Environment details (Python version, OS, database)

### Suggesting Features

Feature requests are welcome! Please open an issue and include:
- A clear description of the feature
- The problem it solves
- Any relevant examples or mockups

### Code Contributions

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** — ensure they follow the existing code style
3. **Test your changes** — verify the application runs correctly
4. **Commit with a clear message** — follow conventional commit style if possible
5. **Push to your fork** and open a Pull Request

#### Pull Request Guidelines
- Keep changes focused and minimal
- Do not modify business logic unless explicitly requested
- Update documentation if you change functionality
- Ensure all existing routes and features still work

## Development Setup

```bash
# Clone your fork
git clone https://github.com/<your-username>/daily_c_s.git
cd daily_c_s

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run the app
python app.py
```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines
- Use meaningful variable and function names
- Add docstrings to helper functions and complex logic
- Keep routes organized by feature (Auth, Dashboard, Customer, etc.)
- Use SQLAlchemy ORM — avoid raw SQL where possible

## Questions?

Feel free to open an issue for any questions about contributing.

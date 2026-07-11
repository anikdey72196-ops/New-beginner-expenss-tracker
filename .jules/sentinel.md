## 2024-07-10 - [Fix] Hardcoded Flask Secret Key
**Vulnerability:** The Flask application `app.py` contained a hardcoded `app.secret_key = "your_secret_key"`.
**Learning:** Hardcoded secret keys allow attackers to forge session cookies, leading to unauthorized access and session hijacking.
**Prevention:** Always use environment variables for sensitive configuration like secret keys, with a secure fallback like `os.urandom(24)` if necessary.

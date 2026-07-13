## 2024-07-10 - [Fix] Hardcoded Flask Secret Key
**Vulnerability:** The Flask application `app.py` contained a hardcoded `app.secret_key = "your_secret_key"`.
**Learning:** Hardcoded secret keys allow attackers to forge session cookies, leading to unauthorized access and session hijacking.
**Prevention:** Always use environment variables for sensitive configuration like secret keys, with a secure fallback like `os.urandom(24)` if necessary.

## 2024-07-11 - [Fix] Missing Global CSRF Protection and Unsafe GET State Mutation
**Vulnerability:** The Flask application `app.py` lacked CSRF protection on forms, and the `/delete_expense/<int:id>` endpoint allowed state mutations via GET requests, which could lead to cross-site request forgery attacks enabling unauthorized expense deletion.
**Learning:** State-changing actions like deletes must never be exposed via GET routes as they can be triggered trivially (e.g., via `<img>` tags). Furthermore, global CSRF protection ensures all POST/PUT/DELETE requests validate a token matching the session.
**Prevention:** Use POST for all state-changing endpoints and employ a library like `flask_wtf.csrf.CSRFProtect` alongside passing `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in all forms.

## 2024-07-12 - [Fix] Inadequate Expense Amount Validation (NaN, Infinity, Negative)
**Vulnerability:** The application previously relied solely on Python's `float()` to validate expense amounts. `float()` accepts inputs like `"inf"`, `"nan"`, and negative numbers, which could be exploited to bypass logical checks, corrupt financial calculations (like dashboard stats or total tracking), or cause unexpected logic crashes when dealing with extreme values.
**Learning:** Never assume type coercion functions like `float()` act as comprehensive boundary validators. Python's `float()` is particularly forgiving and accommodates non-finite representations, which can cause subtle logic bugs if persisted in databases without further checks.
**Prevention:** Implement explicit boundary and finite checks (`math.isinf()`, `math.isnan()`, `>= 0`, `<= upper_limit`) after converting strings to floats, especially in financial or counting contexts.

## 2026-07-13 - [Fix] Insecure Database Connections (MitM Risk)
**Vulnerability:** The application configured SQLAlchemy to connect to external databases using `ssl.CERT_NONE` and `check_hostname: False`. This completely disabled SSL certificate validation, rendering the application vulnerable to Man-in-the-Middle (MitM) attacks where an attacker could intercept and potentially modify sensitive database traffic.
**Learning:** Managed database services (like Aiven.io, which this project uses) require SSL. However, explicitly disabling certificate verification defeats the purpose of SSL. When connecting to managed databases, we must use the correct CA bundle path to verify the identity of the database server securely.
**Prevention:** Always enforce `ssl.CERT_REQUIRED` and `check_hostname: True` for database connections outside of localhost. Explicitly specify the CA bundle path (e.g., `/etc/pki/tls/certs/ca-bundle.crt` for Amazon Linux/Vercel environments) to ensure the server's certificate can be properly verified.

## 2024-07-10 - [Fix] Hardcoded Flask Secret Key
**Vulnerability:** The Flask application `app.py` contained a hardcoded `app.secret_key = "your_secret_key"`.
**Learning:** Hardcoded secret keys allow attackers to forge session cookies, leading to unauthorized access and session hijacking.
**Prevention:** Always use environment variables for sensitive configuration like secret keys, with a secure fallback like `os.urandom(24)` if necessary.

## 2024-07-11 - [Fix] Missing Global CSRF Protection and Unsafe GET State Mutation
**Vulnerability:** The Flask application `app.py` lacked CSRF protection on forms, and the `/delete_expense/<int:id>` endpoint allowed state mutations via GET requests, which could lead to cross-site request forgery attacks enabling unauthorized expense deletion.
**Learning:** State-changing actions like deletes must never be exposed via GET routes as they can be triggered trivially (e.g., via `<img>` tags). Furthermore, global CSRF protection ensures all POST/PUT/DELETE requests validate a token matching the session.
**Prevention:** Use POST for all state-changing endpoints and employ a library like `flask_wtf.csrf.CSRFProtect` alongside passing `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>` in all forms.

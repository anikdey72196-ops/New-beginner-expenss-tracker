import csv
import os
import uuid
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.csv')
EXPENSES_FILE = os.path.join(BASE_DIR, 'expenses.csv')

def init_csv():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'name', 'password'])
            
    if not os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'email', 'amount', 'category', 'date', 'description'])

def add_user(email, name, password):
    with open(USERS_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([email, name, password])

def get_user_by_email(email):
    if not os.path.exists(USERS_FILE): return None
    with open(USERS_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                return row
    return None

def add_expense(email, amount, category, date, description):
    expense_id = str(uuid.uuid4())
    with open(EXPENSES_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([expense_id, email, amount, category, date, description])
    return expense_id

def get_expenses_by_user(email):
    if not os.path.exists(EXPENSES_FILE): return []
    expenses = []
    with open(EXPENSES_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                expenses.append(row)
    return expenses

def get_expense_by_id(expense_id, email):
    if not os.path.exists(EXPENSES_FILE): return None
    with open(EXPENSES_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == expense_id and row['email'] == email:
                return row
    return None

def update_expense(expense_id, email, amount, category, date, description):
    if not os.path.exists(EXPENSES_FILE): return False
    expenses = []
    updated = False
    with open(EXPENSES_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == expense_id and row['email'] == email:
                row['amount'] = amount
                row['category'] = category
                row['date'] = date
                row['description'] = description
                updated = True
            expenses.append(row)
    
    if updated:
        with open(EXPENSES_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'email', 'amount', 'category', 'date', 'description'])
            for exp in expenses:
                writer.writerow([exp['id'], exp['email'], exp['amount'], exp['category'], exp['date'], exp['description']])
    return updated

def delete_expense(expense_id, email):
    if not os.path.exists(EXPENSES_FILE): return False
    expenses = []
    deleted = False
    with open(EXPENSES_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['id'] == expense_id and row['email'] == email:
                deleted = True
            else:
                expenses.append(row)
    
    if deleted:
        with open(EXPENSES_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'email', 'amount', 'category', 'date', 'description'])
            for exp in expenses:
                writer.writerow([exp['id'], exp['email'], exp['amount'], exp['category'], exp['date'], exp['description']])
    return deleted

GOOD_CATEGORIES = {'Education', 'Health', 'Utilities', 'Software', 'Personal Care'}
BAD_CATEGORIES = {'Shopping', 'Entertainment', 'Party/junk food'}

def get_dashboard_stats(email):
    expenses = get_expenses_by_user(email)
    
    if not expenses:
        return {
            'overall_score': 5.0,
            'today_score': 50,
            'last_month_total': 0.0,
            'daily_avg_score': 5.0
        }
        
    overall_score = 5.0
    today_score = 50
    last_month_total = 0.0
    
    today = datetime.date.today()
    try:
        first_of_this_month = today.replace(day=1)
        last_day_last_month = first_of_this_month - datetime.timedelta(days=1)
        first_of_last_month = last_day_last_month.replace(day=1)
    except:
        
        first_of_last_month = today
        last_day_last_month = today
    
    daily_scores = {}
    
    for exp in expenses:
        category = exp.get('category', '')
        try:
            amount = float(exp.get('amount', 0))
        except ValueError:
            amount = 0.0
            
        date_str = exp.get('date', '')
        
        try:
            exp_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            exp_date = today
            
        # Overall score logic (+1 good, -2 bad)
        if category in GOOD_CATEGORIES:
            overall_score += 1
        elif category in BAD_CATEGORIES:
            overall_score -= 2
            
        # Today's score (starts at 50, +10 good, -20 bad, out of 100)
        if exp_date == today:
            if category in GOOD_CATEGORIES:
                today_score += 10
            elif category in BAD_CATEGORIES:
                today_score -= 20
                
        # Last month total expenses
        if first_of_last_month <= exp_date <= last_day_last_month:
            last_month_total += amount
            
        # Daily tracking for average
        if exp_date not in daily_scores:
            daily_scores[exp_date] = 5.0
        if category in GOOD_CATEGORIES:
            daily_scores[exp_date] += 1
        elif category in BAD_CATEGORIES:
            daily_scores[exp_date] -= 2

    # Clamping scores to bounds
    overall_score = max(0.0, min(10.0, overall_score))
    today_score = max(0, min(100, today_score))
    
    # Calculate daily average score
    if daily_scores:
        avg = sum(max(0.0, min(10.0, s)) for s in daily_scores.values()) / len(daily_scores)
        daily_avg_score = round(avg, 1)
    else:
        daily_avg_score = 5.0

    return {
        'overall_score': round(overall_score, 1),
        'today_score': today_score,
        'last_month_total': round(last_month_total, 2),
        'daily_avg_score': daily_avg_score
    }


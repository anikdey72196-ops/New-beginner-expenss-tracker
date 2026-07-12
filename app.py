import os
import math
import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, redirect, session, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from form import RegistrationForm, LoginForm
from extensions import db
from models import User, Expense

app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

GOOD_CATEGORIES = {'Education', 'Health', 'Utilities', 'Software', 'Personal Care'}
BAD_CATEGORIES = {'Shopping', 'Entertainment', 'Party/junk food'}

def get_dashboard_stats(expenses):
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
    except Exception:
        first_of_last_month = today
        last_day_last_month = today
    
    daily_scores = {}
    
    for exp in expenses:
        category = exp.category
        amount = exp.amount
        exp_date = exp.date
            
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


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Store user in database
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash("Username already exists", "danger")
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data,
                password_hash=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Registered successfully!", "success")
            return redirect(url_for('login'))
    return render_template('register.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Find the user by their username
            user = User.query.filter_by(username=form.username.data).first()
            
            # If the user doesn't exist, or password doesn't match
            if not user or not check_password_hash(user.password_hash, form.password.data):
                flash("Invalid credentials", "danger")
                return redirect(url_for('login'))
            
            # If successful
            session['user_id'] = user.id
            session['user'] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/home', methods=['GET'])
def home():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    
    # Get expenses for the logged in user to display on the dashboard
    user_id = session.get('user_id')
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    expenses_list = [exp.to_dict() for exp in expenses]
    stats = get_dashboard_stats(expenses)
    
    # Calculate weekly spending
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())

    weekly_spending = {i: 0.0 for i in range(7)}
    category_totals = {}

    for exp in expenses:
        # Weekly spending
        if start_of_week <= exp.date <= start_of_week + datetime.timedelta(days=6):
            day_idx = exp.date.weekday()
            weekly_spending[day_idx] += exp.amount

        # Category totals (all time)
        category_totals[exp.category] = category_totals.get(exp.category, 0.0) + exp.amount

    max_spend = max(weekly_spending.values()) if weekly_spending else 0

    chart_data = []
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    for i in range(7):
        amount = weekly_spending[i]
        # h-64 in tailwind is 16rem = 256px
        # We use percentage for height
        height_pct = (amount / max_spend * 100) if max_spend > 0 else 5
        height_pct = max(height_pct, 5)  # min 5% height to be visible
        chart_data.append({
            'day': days[i],
            'amount': round(amount, 2),
            'height_pct': int(height_pct),
            'is_today': (start_of_week + datetime.timedelta(days=i)) == today
        })

    # Top Categories
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:4]

    category_info = {
        'Education': {'icon': 'school', 'color_class': 'text-blue-400', 'bg_class': 'bg-blue-400/10'},
        'Health': {'icon': 'monitor_heart', 'color_class': 'text-red-400', 'bg_class': 'bg-red-400/10'},
        'Utilities': {'icon': 'bolt', 'color_class': 'text-yellow-400', 'bg_class': 'bg-yellow-400/10'},
        'Software': {'icon': 'terminal', 'color_class': 'text-green-400', 'bg_class': 'bg-green-400/10'},
        'Personal Care': {'icon': 'self_improvement', 'color_class': 'text-pink-400', 'bg_class': 'bg-pink-400/10'},
        'Shopping': {'icon': 'shopping_bag', 'color_class': 'text-purple-400', 'bg_class': 'bg-purple-400/10'},
        'Entertainment': {'icon': 'movie', 'color_class': 'text-orange-400', 'bg_class': 'bg-orange-400/10'},
        'Party/junk food': {'icon': 'local_pizza', 'color_class': 'text-amber-400', 'bg_class': 'bg-amber-400/10'}
    }

    top_categories = []
    for cat, total in sorted_categories:
        info = category_info.get(cat, {'icon': 'category', 'color_class': 'text-zinc-400', 'bg_class': 'bg-zinc-700/20'})
        top_categories.append({
            'name': cat,
            'total': round(total, 2),
            'icon': info['icon'],
            'color_class': info['color_class'],
            'bg_class': info['bg_class']
        })

    return render_template('home.html', username=session['user'], expenses=expenses_list, stats=stats, chart_data=chart_data, top_categories=top_categories)

@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Retrieve form data
        amount = request.form.get('amount')
        category = request.form.get('category')
        date_str = request.form.get('date') 
        description = request.form.get('description')
        
        try:
            amount_val = float(amount)
            if math.isnan(amount_val) or math.isinf(amount_val) or amount_val < 0 or amount_val > 1000000000:
                raise ValueError
        except (ValueError, TypeError):
            flash("Invalid amount", "danger")
            return redirect(url_for('addexpense'))
            
        try:
            exp_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            exp_date = datetime.date.today()
        
        new_expense = Expense(
            user_id=session['user_id'],
            amount=amount_val,
            category=category,
            date=exp_date,
            description=description
        )
        db.session.add(new_expense)
        db.session.commit()
        
        flash("Expense added successfully!", "success")
        return redirect(url_for('home'))
        
    return render_template("add_expense.html")

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
        
    # Get the specific expense
    expense = Expense.query.filter_by(id=id, user_id=session['user_id']).first()
    if not expense:
        flash("Expense not found", "danger")
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')
        date_str = request.form.get('date')
        description = request.form.get('description')
        
        try:
            amount_val = float(amount)
            if math.isnan(amount_val) or math.isinf(amount_val) or amount_val < 0 or amount_val > 1000000000:
                raise ValueError
            expense.amount = amount_val
        except (ValueError, TypeError):
            flash("Invalid amount", "danger")
            return redirect(url_for('edit_expense', id=id))
            
        expense.category = category
        try:
            expense.date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass # keep original if invalid
            
        expense.description = description
        db.session.commit()
        
        flash("Expense updated successfully!", "success")
        return redirect(url_for('home'))
        
    return render_template("edit.html", expense=expense.to_dict())

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
        
    expense = Expense.query.filter_by(id=id, user_id=session['user_id']).first()
    if expense:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted successfully!", "success")
    else:
        flash("Expense not found or could not be deleted.", "danger")
        
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)
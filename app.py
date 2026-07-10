from flask import Flask,render_template,redirect,session,request,url_for,flash
from form import Registration,login as loginform
import csv_db


app = Flask(__name__)
app.secret_key = 'your_secret_key'

csv_db.init_csv()

@app.route("/",methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form = Registration()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Store user in CSV database
            csv_db.add_user(
                email=form.email.data,
                name=form.username.data,
                password=form.password.data
            )
            flash("Registered successfully!", "success")
            return redirect(url_for('login'))
    return render_template('register.html', form=form)
    
@app.route('/login',methods=['GET','POST'])
def login():
    form = loginform()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Find the user by their email in our CSV database
            user = csv_db.get_user_by_email(form.email.data)
            
            # If the user doesn't exist, or password doesn't match
            if not user or user['password'] != form.password.data:
                flash("Invalid credentials", "danger")
                return redirect(url_for('login'))
            
            # If successful
            session['user'] = user['name']
            session['email'] = user['email']
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/home',methods=['GET'])
def home():
    if 'user' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    
    # Get expenses for the logged in user to display on the dashboard
    user_email = session.get('email', '')
    expenses = csv_db.get_expenses_by_user(user_email)
    stats = csv_db.get_dashboard_stats(user_email)
    
    return render_template('home.html', username=session['user'], expenses=expenses, stats=stats)

@app.route('/addexpense',methods=['GET','POST'])
def addexpense():
    if 'user' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Retrieve form data
        amount = request.form.get('amount')
        category = request.form.get('category')
        date = request.form.get('date') 
        description = request.form.get('description')
        
        # Add the expense to CSV
        csv_db.add_expense(session['email'], amount, category, date, description)
        flash("Expense added successfully!", "success")
        return redirect(url_for('home'))
        
    return render_template("Add expense.html")

@app.route('/edit_expense/<id>', methods=['GET', 'POST'])
def edit_expense(id):
    if 'user' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
        
    # Get the specific expense
    expense = csv_db.get_expense_by_id(id, session['email'])
    if not expense:
        flash("Expense not found", "danger")
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')
        date = request.form.get('date')
        description = request.form.get('description')
        
        # Update the expense
        csv_db.update_expense(id, session['email'], amount, category, date, description)
        flash("Expense updated successfully!", "success")
        return redirect(url_for('home'))
        
    return render_template("edit.html", expense=expense)

@app.route('/delete_expense/<id>', methods=['GET', 'POST'])
def delete_expense(id):
    if 'user' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
        
    if csv_db.delete_expense(id, session['email']):
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
    app.run(debug=True)
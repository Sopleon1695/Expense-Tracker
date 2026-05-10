from flask import Flask , render_template , request , redirect
import sqlite3
import re
from werkzeug.security import generate_password_hash,check_password_hash
import uuid
app=Flask(__name__)

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    #  Get all expenses
    cursor.execute("SELECT id, name, category, amount FROM expenses ORDER BY id DESC")
    transactions = cursor.fetchall()

    # Calculate totals
    total_income = 0
    total_expense = 0

    for _, name, category, amount in transactions:
        if category.lower() == "saving":
            total_income += amount
        else:
            total_expense += amount

    balance = total_income - total_expense

    conn.close()

    return render_template(
        "dashboard.html",
        income=total_income,
        expense=total_expense,
        balance=balance,
        transactions=transactions   #  Imp
    )

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):
            return redirect("/dashboard")
        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    message = None
    reset_link = None

    if request.method == "POST":
        email = request.form["email"]

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user:
            token = str(uuid.uuid4())
            reset_link = f"/reset/{token}"

            message = "Success: Reset link generated!"
        else:
            message = "Error: Email not found!"

    return render_template("forgot.html", message=message, link=reset_link)

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    message = None
    redirect_to_login = False

    if request.method == "POST":
        new_password = request.form["password"]
        confirm = request.form["confirm"]

        if new_password != confirm:
            message = "Error: Passwords do not match!"
            return render_template("reset.html", message=message)

        hashed = generate_password_hash(new_password)

        # ⚠️ TEMP (simple version)
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET password = ?", (hashed,))
        conn.commit()
        conn.close()

        message = "Success: Password updated successfully!"
        redirect_to_login = True

    return render_template("reset.html", message=message, redirect=redirect_to_login)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = None
    redirect_to_login = False
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message = "error: Invalid email format"
            return render_template("signup.html", message=message)

        if password != confirm:
            message = "error: Passwords do not match"
            return render_template("signup.html", message=message)
        
        #  Hash password
        hashed_password = generate_password_hash(password)

        # (test)
        print("Name:", name)
        print("Email:", email)
        print("Hashed Password:", hashed_password)

        # save to database
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()

            message = "success: User registered successfully!"
            redirect_to_login = True  
            

            # #  DEBUG CHECK
            # cursor.execute("SELECT * FROM users")
            # print("USERS:", cursor.fetchall())

        except:
            message= "Error: Email already exists!"

        conn.close()

    return render_template("signup.html", message=message, redirect=redirect_to_login)


@app.route("/home")
def home():
    
    conn=sqlite3.connect("expenses.db")
    cursor=conn.cursor()

    cursor.execute("SELECT * FROM expenses")    
    expenses = cursor.fetchall()

    # formatted_expenses =[]
    # for e in expenses:
    #     formatted_amount= f"MMK {e[3]:,}"
    #     formatted_expenses.append((e[0], e[1], e[2], formatted_amount))
        

    # total = sum(expense[2] for expense in expenses)

    category_totals={}

    for expense in expenses:
        category = expense[2]
        amount = int(expense[3])

        if category in category_totals:
            category_totals[category] += amount

        else:
            category_totals[category] = amount
    
    # sorting
    sorted_totals =  sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )
    # chart data 
    labels = [item[0] for item in sorted_totals]
    values = [item[1] for item in sorted_totals]
    
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0
    formatted_total=f"MMK {total:,}"

    #fetchall ->many rows
    #fetchone ->single row



    conn.close()
    return render_template("index.html", 
                           expenses=expenses, 
                           total = formatted_total , 
                           category_totals = sorted_totals,
                           labels = labels,
                           values = values
    )


#add expenses
@app.route("/add", methods=["POST"])
def add():

    expense = request.form["expense"] #must same from index form
    category = request.form["category"]
    amount = int(request.form["amount"])

    conn= sqlite3.connect("expenses.db")
    cursor= conn.cursor()

    cursor.execute("INSERT INTO expenses (name, category,amount) " \
    "VALUES (? , ?, ?)" , (expense, category, amount))

    print("Expense :", expense)
    print("Amount :", amount)

    conn.commit()
    conn.close()

    # return "Expense successfully added!"
    return redirect("/")



#create database
def init_db():
    conn =  sqlite3.connect("expenses.db")
    cursor =  conn.cursor()

    # 📊 Expenses table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS expenses (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   category TEXT, 
                   amount INTEGER)""")
    
    # 👤 Users table (ADD THIS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    
    conn.commit()
    conn.close()

init_db()


#edit
@app.route("/edit/<int:id>")
def edit(id):

    conn= sqlite3.connect("expenses.db")
    cursor= conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?" , (id,))
    expense= cursor.fetchone()

    conn.close()

    return render_template("edit.html",expense=expense)
# delete 
@app.route("/delete/<int:id>")
def delete(id):

    conn= sqlite3.connect("expenses.db")
    cursor=conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

#Update
@app.route("/update/<int:id>" , methods= ["POST"])
def update(id):

    expense= request.form["expense"]
    category= request.form["category"]
    amount= int(request.form["amount"])

    conn = sqlite3.connect("expenses.db")
    cursor= conn.cursor()

    cursor.execute(
        "UPDATE expenses SET name= ? , category= ?, amount = ? WHERE id = ?",
        (expense, category, amount , id)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)


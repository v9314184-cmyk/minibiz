from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("minibiz_web.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        description TEXT,
        amount REAL
    )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("minibiz_web.db")
    cursor = conn.cursor()

    if request.method == "POST":
        entry_type = request.form["type"]
        description = request.form["description"]
        amount = float(request.form["amount"])
        date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("INSERT INTO records (date, type, description, amount) VALUES (?, ?, ?, ?)",
                       (date, entry_type, description, amount))
        conn.commit()

    cursor.execute("SELECT * FROM records")
    records = cursor.fetchall()

    income = sum(r[4] for r in records if r[2] == "Income")
    expense = sum(r[4] for r in records if r[2] == "Expense")
    profit = income - expense

    conn.close()

    return render_template_string("""
    <h1>MiniBiz Manager (Web)</h1>
    <form method="POST">
        <select name="type">
            <option value="Income">Income</option>
            <option value="Expense">Expense</option>
        </select>
        <input name="description" placeholder="Description" required>
        <input name="amount" type="number" step="0.01" placeholder="Amount" required>
        <button type="submit">Add</button>
    </form>

    <h2>Records</h2>
    {% for r in records %}
        <p>{{r[1]}} | {{r[2]}} | {{r[3]}} | ₹{{r[4]}}</p>
    {% endfor %}

    <h2>Summary</h2>
    <p>Income: ₹{{income}}</p>
    <p>Expense: ₹{{expense}}</p>
    <h3>Profit: ₹{{profit}}</h3>
    """, records=records, income=income, expense=expense, profit=profit)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

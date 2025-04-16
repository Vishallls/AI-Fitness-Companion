from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import datetime

app = Flask(__name__)

# Database setup
def setup_database():
    conn = sqlite3.connect("fitness_companion.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS workout_logs (
                        id INTEGER PRIMARY KEY,
                        date TEXT,
                        exercise TEXT,
                        duration INTEGER,
                        calories REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
                        id INTEGER PRIMARY KEY,
                        goal_type TEXT,
                        goal_value REAL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log_workout():
    data = request.form
    conn = sqlite3.connect("fitness_companion.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO workout_logs (date, exercise, duration, calories) VALUES (?, ?, ?, ?)",
                   (data['date'], data['exercise'], int(data['duration']), float(data['calories'])))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/progress')
def progress():
    conn = sqlite3.connect("fitness_companion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, SUM(calories) FROM workout_logs GROUP BY date")
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/recommendation')
def recommendation():
    conn = sqlite3.connect("fitness_companion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(calories) FROM workout_logs")
    avg = cursor.fetchone()[0] or 0
    conn.close()
    
    if avg < 300:
        msg = "Increase workout intensity or duration!"
    elif avg < 500:
        msg = "You're on track. Keep it up!"
    else:
        msg = "Great job! Consider adding variety to your routine."
    
    return jsonify({'message': msg})

@app.route('/set_goal', methods=['POST'])
def set_goal():
    data = request.form
    conn = sqlite3.connect("fitness_companion.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO goals (goal_type, goal_value) VALUES (?, ?)",
                   (data['goal_type'], float(data['goal_value'])))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)

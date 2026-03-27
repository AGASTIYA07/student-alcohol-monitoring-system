import sqlite3
import datetime
import os
import random
import serial
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# If running on Render with a mounted disk at /data, save there. Otherwise save locally.
DB_FILE = '/data/students.db' if os.path.exists('/data') else 'students.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_FILE):
        conn = get_db_connection()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

init_db()

def get_last_n_records(student_id, limit=7):
    conn = get_db_connection()
    records = conn.execute(
        'SELECT * FROM records WHERE student_id = ? ORDER BY timestamp DESC LIMIT ?',
        (student_id, limit)
    ).fetchall()
    conn.close()
    return records

def calculate_clean_streak(student_id):
    conn = get_db_connection()
    records = conn.execute(
        'SELECT * FROM records WHERE student_id = ? ORDER BY timestamp DESC',
        (student_id,)
    ).fetchall()
    conn.close()
    
    streak = 0
    for row in records:
        if row['alcohol_level'] == 0:
            streak += 1
        else:
            break
    return streak

def get_avoidance_status(student_id):
    records = get_last_n_records(student_id, 1)
    if not records:
        return False
    last_record_date = datetime.datetime.strptime(records[0]['timestamp'], "%Y-%m-%d %H:%M:%S")
    days_since = (datetime.datetime.now() - last_record_date).days
    return days_since > 3  # Avoidance marked after 3 days of no readings.

def analyze_student(student_id, current_level=None):
    records = get_last_n_records(student_id, 7)
    
    score = 0
    classification = "SAFE"
    suggestion = "Keep up the great work! You are on a safe path."
    prediction = "Low probability of future risks."
    escalation = "None"
    
    # Base analysis variables
    high_count_total = 0
    high_count_week = 0
    consistent_count = 0
    
    now = datetime.datetime.now()
    
    # Get all records to measure overall escalation
    conn = get_db_connection()
    all_records = conn.execute(
        'SELECT * FROM records WHERE student_id = ? ORDER BY timestamp DESC',
        (student_id,)
    ).fetchall()
    conn.close()
    
    for r in all_records:
        if r['alcohol_level'] > 200:
            high_count_total += 1
            t = datetime.datetime.strptime(r['timestamp'], "%Y-%m-%d %H:%M:%S")
            if (now - t).days <= 7:
                high_count_week += 1

    # Analyze last 7 items for consistency
    for r in records:
        if r['alcohol_level'] > 50:
            consistent_count += 1
            
    # Include the current level in active assessment if provided
    active_level = current_level if current_level is not None else (records[0]['alcohol_level'] if records else 0)

    is_class_hours = False
    current_hour = now.hour
    if 9 <= current_hour < 16:  # 9 AM to 4 PM
        is_class_hours = True
        
    # Logic: Classification
    if active_level > 200:
        classification = "HIGH RISK"
        score += 20
        suggestion = "Immediate counseling and support is recommended."
    elif consistent_count >= 5 or (active_level > 50 and consistent_count >= 4):
        classification = "CONSISTENT"
        score += 10
        suggestion = "Habit-forming behavior detected. Consider habit reduction strategies."
    elif active_level > 0:
        classification = "OCCASIONAL"
        score += 5
        suggestion = "Caution advised. Try to maintain zero consumption."
    else:
        classification = "SAFE"
        
    # Consistency penalty
    if consistent_count >= 3:
        score += 10
        
    # Time violation
    if is_class_hours and active_level > 0:
        score += 15
        
    # Normalize score
    score = min(score + (high_count_total * 5), 100)
    
    # Prediction
    recent_high_consistent = sum(1 for r in records[:3] if r['alcohol_level'] > 50)
    if current_level is not None and current_level > 50:
        recent_high_consistent += 1
        
    if recent_high_consistent >= 3:
        prediction = "High probability of repeated behavior. Intervention required."

    # Escalation
    if high_count_total >= 5:
        escalation = "Mandatory counseling flag"
    elif high_count_week >= 3:
        escalation = "Faculty alert triggered"
    elif high_count_total >= 1:
        escalation = "Warning issued"
        
    avoidance = get_avoidance_status(student_id)
    streak = calculate_clean_streak(student_id)
    
    return {
        "classification": classification,
        "score": score,
        "suggestion": suggestion,
        "prediction": prediction,
        "escalation": escalation,
        "avoidance": avoidance,
        "clean_streak": streak,
        "is_class_hours": is_class_hours
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/faculty')
def faculty():
    return render_template('faculty.html')

@app.route('/api/read_sensor', methods=['GET'])
def read_sensor():
    # Attempt to read from Arduino Serial (e.g., COM3 on Windows, /dev/tty.usbmodem on Mac)
    # Since we don't know the exact port, we try a common one, or fallback to mock data
    SERIAL_PORT = '/dev/tty.usbmodem14101' # Change to appropriate port depending on device
    BAUD_RATE = 9600
    try:
        # Note: In a real environment, you'd keep the serial connection open. 
        # Opening/closing for every request resets Arduino.
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        line = ser.readline().decode('utf-8').strip()
        ser.close()
        
        if line.isdigit():
            level = int(line)
        else:
            level = 0
            
        return jsonify({"success": True, "level": level, "mocked": False})
    except Exception as e:
        # Fallback to simulated MQ-3 reading if no hardware is attached yet
        # Let's generate a mostly safe mock, but sometimes elevated
        mock_level = random.choice([0, 0, 0, 0, 25, 60, 220])
        return jsonify({
            "success": True, 
            "level": mock_level, 
            "mocked": True, 
            "message": "Hardware disconnected. Using simulated sensor data."
        })

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    student_id = data.get('student_id')
    alcohol_level = int(data.get('alcohol_level', 0))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO records (student_id, alcohol_level) VALUES (?, ?)',
                 (student_id, alcohol_level))
    conn.commit()
    conn.close()
    
    analysis = analyze_student(student_id, alcohol_level)
    return jsonify(analysis)

@app.route('/api/history/<student_id>')
def history(student_id):
    records = get_last_n_records(student_id, 20)  # past 20 for chart
    
    # Reverse to show chronological order
    data = []
    labels = []
    for r in reversed(records):
        data.append(r['alcohol_level'])
        # Extract just time or short date
        dt = datetime.datetime.strptime(r['timestamp'], "%Y-%m-%d %H:%M:%S")
        labels.append(dt.strftime("%d %b %H:%M"))

    analysis = analyze_student(student_id)

    return jsonify({
        "labels": labels,
        "data": data,
        "analysis": analysis
    })

@app.route('/api/all_students')
def all_students():
    conn = get_db_connection()
    students_rows = conn.execute('SELECT DISTINCT student_id FROM records').fetchall()
    
    students_data = []
    for row in students_rows:
        sid = row['student_id']
        analysis = analyze_student(sid)
        students_data.append({
            "student_id": sid,
            "classification": analysis["classification"],
            "score": analysis["score"],
            "streak": analysis["clean_streak"],
            "avoidance": analysis["avoidance"],
            "escalation": analysis["escalation"]
        })
    conn.close()
    
    return jsonify(students_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

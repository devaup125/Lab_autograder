from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import sqlite3, subprocess, bcrypt, time

app = Flask(__name__)
app.secret_key = "secret"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("lab.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- LOGIN ----------------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM students WHERE username=?", (u,)).fetchone()

        if user and bcrypt.checkpw(p.encode(), user['password_hash']):
            session['uid'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']  # 🔥 ADD ROLE

            if user['role'] == 'admin':
                return redirect('/admin')

            return redirect('/problems')

    return render_template('login.html')


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt())

        conn = get_db()
        conn.execute("INSERT INTO students(username,password_hash,role) VALUES(?,?,?)",
                     (u,p,'student'))
        conn.commit()

        return redirect('/')

    return render_template('register.html')


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/')

    conn = get_db()

    problems = conn.execute("SELECT * FROM problems").fetchall()

    scores = conn.execute("""
        SELECT s.username,
               COUNT(sub.id) as attempts,
               SUM(sub.score) as total_score,
               SUM(sub.penalty) as total_penalty,
               MAX(sub.timestamp) as last_submission
        FROM students s
        LEFT JOIN submissions sub ON s.id=sub.student_id
        GROUP BY s.id
        ORDER BY total_score DESC
    """).fetchall()

    return render_template("base_admin.html", problems=problems, scores=scores)


# ---------------- PROBLEMS ----------------
@app.route('/problems')
def problems():
    conn = get_db()
    data = conn.execute("SELECT * FROM problems").fetchall()
    return render_template('problems.html', problems=data)


@app.route('/problem/<int:pid>')
def problem(pid):
    conn = get_db()
    p = conn.execute("SELECT * FROM problems WHERE id=?", (pid,)).fetchone()
    return render_template('problem.html', problem=p)


# ---------------- SUBMIT ----------------
@app.route('/submit/<int:pid>', methods=['POST'])
def submit(pid):
    if 'uid' not in session:
        return jsonify({"error": "Login required"})

    code = request.form['code']
    lang = request.form['language']

    start_time = time.time()

    with open("temp.py","w") as f:
        f.write(code)

    try:
        result = subprocess.run(
            ["python", "temp.py"],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"})

    exec_time = round(time.time() - start_time, 3)

    # SCORING
    if error:
        score = 0
        penalty = 5
        status = "ERROR"
    else:
        score = 10
        penalty = 0
        status = "SUCCESS"

    # SAVE
    conn = get_db()
    conn.execute("""
        INSERT INTO submissions(student_id,problem_id,code,language,score,penalty)
        VALUES(?,?,?,?,?,?)
    """,(session['uid'], pid, code, lang, score, penalty))
    conn.commit()

    return jsonify({
        "output": output,
        "error": error,
        "score": score,
        "penalty": penalty,
        "status": status,
        "time": exec_time
    })


# ---------------- SCOREBOARD ----------------
@app.route('/scoreboard')
def scoreboard():
    conn = get_db()

    data = conn.execute("""
        SELECT s.username,
               COUNT(sub.id) as attempts,
               SUM(sub.score) as total_score,
               SUM(sub.penalty) as total_penalty,
               MAX(sub.timestamp) as last_submission
        FROM students s
        LEFT JOIN submissions sub ON s.id=sub.student_id
        GROUP BY s.id
        ORDER BY total_score DESC
    """).fetchall()

    return render_template('scoreboard.html', scores=data)


# ---------------- STUDENT HISTORY ----------------
@app.route('/history')
def history():
    if 'uid' not in session:
        return redirect('/')

    conn = get_db()

    data = conn.execute("""
        SELECT p.title, sub.score, sub.penalty, sub.timestamp
        FROM submissions sub
        JOIN problems p ON p.id = sub.problem_id
        WHERE sub.student_id=?
        ORDER BY sub.timestamp DESC
    """, (session['uid'],)).fetchall()

    return render_template('student_history.html', subs=data)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
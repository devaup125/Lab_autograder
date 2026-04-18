from flask import Flask, render_template, request, redirect, session, jsonify
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
            session['role'] = user['role']   # 🔥 IMPORTANT

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

        # 🔥 CHECK IF USER EXISTS
        existing = conn.execute(
            "SELECT * FROM students WHERE username=?", (u,)
        ).fetchone()

        if existing:
            return render_template("register.html", error="Username already exists ❌")

        # INSERT NEW USER
        conn.execute(
            "INSERT INTO students(username,password_hash,role) VALUES(?,?,?)",
            (u, p, 'student')
        )
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

    # 🔥 FIX: use proper template
    return render_template("base_admin.html",
                           problems=problems,
                           scores=scores)
@app.route('/admin/add_problem', methods=['GET','POST'])
def add_problem():

    if session.get('role') != 'admin':
        return redirect('/')

    conn = get_db()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        language = request.form['language']

        conn.execute(
            "INSERT INTO problems(title, description, language) VALUES(?,?,?)",
            (title, description, language)
        )
        conn.commit()

        return redirect('/admin')   # go back to dashboard

    return render_template('add_problem.html')

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

    code = request.form['code']
    lang = request.form['language']

    conn = get_db()
    testcases = conn.execute(
        "SELECT * FROM testcases WHERE problem_id=?", (pid,)
    ).fetchall()

    passed = 0
    total = len(testcases)

    for t in testcases:

        try:
            if lang == "python":
                result = subprocess.run(
                    ["python", "-c", code],
                    input=t["input"],
                    text=True,
                    capture_output=True,
                    timeout=3
                )

            elif lang == "c":
                with open("temp.c", "w") as f:
                    f.write(code)

                subprocess.run(["gcc", "temp.c", "-o", "temp"])
                result = subprocess.run(
                    ["./temp"],
                    input=t["input"],
                    text=True,
                    capture_output=True
                )

            elif lang == "cpp":
                with open("temp.cpp", "w") as f:
                    f.write(code)

                subprocess.run(["g++", "temp.cpp", "-o", "temp"])
                result = subprocess.run(
                    ["./temp"],
                    input=t["input"],
                    text=True,
                    capture_output=True
                )

            output = result.stdout.strip()

            if output == t["output"].strip():
                passed += 1

        except:
            return jsonify({"error": "Execution failed"})

    score = int((passed / total) * 10)

    # SAVE
    conn.execute("""
        INSERT INTO submissions(student_id,problem_id,code,language,score,penalty)
        VALUES(?,?,?,?,?,?)
    """,(session['uid'], pid, code, lang, score, 0))
    conn.commit()

    return jsonify({
        "passed": passed,
        "total": total,
        "score": score
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


# ---------------- HISTORY ----------------
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
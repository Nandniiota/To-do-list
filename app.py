from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import date, datetime

app = Flask(__name__)


def get_db():

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=DESKTOP-L4LUT88\\SQLEXPRESS;"
        "DATABASE=TodoApp;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


@app.route("/")
def index():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, due_date, priority, completed
        FROM Tasks
        ORDER BY due_date ASC
    """)

    tasks = cursor.fetchall()

    conn.close()

    today = date.today()

    today_tasks = []
    pending_tasks = []
    overdue_tasks = []
    completed_tasks = []

    for task in tasks:

        due_date = task.due_date

        # Convert datetime to date
        if isinstance(due_date, datetime):
            due_date = due_date.date()

        # Completed tasks
        if task.completed:
            completed_tasks.append(task)

        # Today's tasks
        elif due_date == today:
            today_tasks.append(task)

        # Future tasks
        elif due_date > today:
            pending_tasks.append(task)

        # Overdue tasks
        elif due_date < today:
            overdue_tasks.append(task)

    return render_template(
        "index.html",
        today_tasks=today_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completed_tasks=completed_tasks
    )

@app.route("/add", methods=["POST"])
def add_task():

    title = request.form.get("title")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority")

    if not title or not due_date or not priority:
        return redirect(url_for("index"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Tasks
        (title, due_date, priority, completed)
        VALUES (?, ?, ?, 0)
    """, (
        title,
        due_date,
        priority
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Tasks
        SET completed =
            CASE
                WHEN completed = 0 THEN 1
                ELSE 0
            END
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM Tasks
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):

    title = request.form.get("title")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority")

    if not title or not due_date or not priority:
        return redirect(url_for("index"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Tasks
        SET
            title = ?,
            due_date = ?,
            priority = ?
        WHERE id = ?
    """, (
        title,
        due_date,
        priority,
        task_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
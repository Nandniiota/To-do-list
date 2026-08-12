from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import date, datetime

app = Flask(__name__)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=DESKTOP-L4LUT88\\SQLEXPRESS;"
        "DATABASE=TodoApp;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def dashboard():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            due_date,
            priority,
            completed
        FROM Tasks
        ORDER BY due_date ASC
    """)

    tasks = cursor.fetchall()

    conn.close()

    today = date.today()

    # Lists
    today_tasks = []
    pending_tasks = []
    overdue_tasks = []
    completed_tasks = []
    high_priority_tasks = []


    # =================================================
    # SEPARATE TASKS
    # =================================================

    for task in tasks:

        due_date = task.due_date

        # Convert datetime to date
        if isinstance(due_date, datetime):
            due_date = due_date.date()


        # ---------------------------------------------
        # COMPLETED
        # ---------------------------------------------

        if task.completed:

            completed_tasks.append(task)

            continue


        # ---------------------------------------------
        # HIGH PRIORITY
        # ---------------------------------------------

        if str(task.priority).lower() == "high":

            high_priority_tasks.append(task)


        # ---------------------------------------------
        # TODAY
        # ---------------------------------------------

        if due_date == today:

            today_tasks.append(task)


        # ---------------------------------------------
        # PENDING
        # ---------------------------------------------

        elif due_date is not None and due_date > today:

            pending_tasks.append(task)


        # ---------------------------------------------
        # OVERDUE
        # ---------------------------------------------

        elif due_date is not None and due_date < today:

            overdue_tasks.append(task)


    # =================================================
    # STATISTICS
    # =================================================

    total_tasks = len(tasks)

    completed_count = len(completed_tasks)

    pending_count = len(pending_tasks)

    today_count = len(today_tasks)

    overdue_count = len(overdue_tasks)

    high_priority_count = len(high_priority_tasks)


    # =================================================
    # SEND EVERYTHING TO DASHBOARD.HTML
    # =================================================

    return render_template(
        "dashboard.html",

        # All tasks
        tasks=tasks,

        # Task categories
        today_tasks=today_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completed_tasks=completed_tasks,
        high_priority_tasks=high_priority_tasks,

        # Counts
        total_tasks=total_tasks,
        completed_count=completed_count,
        pending_count=pending_count,
        today_count=today_count,
        overdue_count=overdue_count,
        high_priority_count=high_priority_count
    )


# =====================================================
# ADD TASK
# =====================================================

@app.route("/add", methods=["POST"])
def add_task():

    title = request.form.get("title")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority")

    if not title or not due_date or not priority:

        return redirect(url_for("dashboard"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Tasks
        (
            title,
            due_date,
            priority,
            completed
        )
        VALUES (?, ?, ?, 0)
    """, (
        title,
        due_date,
        priority
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =====================================================
# COMPLETE / UNCOMPLETE
# =====================================================

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

    return redirect(url_for("dashboard"))


# =====================================================
# DELETE
# =====================================================

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

    return redirect(url_for("dashboard"))


# =====================================================
# EDIT
# =====================================================

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):

    title = request.form.get("title")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority")

    if not title or not due_date or not priority:

        return redirect(url_for("dashboard"))

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

    return redirect(url_for("dashboard"))


# =====================================================
# RUN DASHBOARD
# =====================================================

if __name__ == "__main__":

    app.run(
        port=5001,
        debug=True
    )
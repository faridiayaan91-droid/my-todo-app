from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Task, TaskHistory
from datetime import datetime

task_bp = Blueprint('task', __name__)

@task_bp.route('/')
def view_tasks():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template('task.html', tasks=tasks)

@task_bp.route('/add', methods=["POST"])
def add_task():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    title = request.form.get('title')
    due_date = request.form.get('due_date')
    if title:
        new_task = Task(
            title=title,
            status="pending",
            due_date=due_date,
            created_at=datetime.utcnow(),
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.flush()
        history = TaskHistory(
            task_id=new_task.id,
            action=f"✅ Task created: '{title}'"
        )
        db.session.add(history)
        db.session.commit()
        flash('Task added successfully', 'success')
    return redirect(url_for('task.view_tasks'))

@task_bp.route('/toggle/<int:task_id>', methods=["POST"])
def toggle_status(task_id):
    task = db.session.get(Task, task_id)
    if task:
        old_status = task.status
        if task.status == 'pending':
            task.status = 'working'
        elif task.status == 'working':
            task.status = 'done'
        else:
            task.status = 'pending'
        history = TaskHistory(
            task_id=task.id,
            action=f"🔄 Status changed: {old_status} → {task.status}"
        )
        db.session.add(history)
        db.session.commit()
    return redirect(url_for('task.view_tasks'))

@task_bp.route('/delete/<int:task_id>', methods=["POST"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted!', 'danger')
    return redirect(url_for('task.view_tasks'))

@task_bp.route('/history/<int:task_id>')
def task_history(task_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    task = db.session.get(Task, task_id)
    history = TaskHistory.query.filter_by(task_id=task_id).order_by(TaskHistory.timestamp.desc()).all()
    return render_template('history.html', task=task, history=history)

@task_bp.route('/clear', methods=["POST"])
def clear_tasks():
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    for task in tasks:
        TaskHistory.query.filter_by(task_id=task.id).delete()
    Task.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    flash('All tasks cleared', 'info')
    return redirect(url_for('task.view_tasks'))
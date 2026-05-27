from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.models import db
from app.models.tasks import Task

taskplanner_bp = Blueprint("taskplanner", __name__)

@taskplanner_bp.route("/task_planner")
@login_required
def task_planner():

    task_data = Task.query.filter_by(
        user_id=current_user.user_id
    ).first()

    # Create empty task record if user has none
    if not task_data:

        task_data = Task(
            user_id=current_user.user_id,
            to_do_morning=[],
            to_do_afternoon=[],
            to_do_evening=[],
            in_progress=[],
            completed=[]
        )

        db.session.add(task_data)
        db.session.commit()

    return render_template(
        "task_planner.html",
        task_data=task_data,
        user=current_user.username
    )


@taskplanner_bp.route(
    "/save_tasks",
    methods=["POST"]
)
@login_required
def save_tasks():

    data = request.get_json()

    task_data = Task.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if not task_data:

        task_data = Task(
            user_id=current_user.user_id
        )

        db.session.add(task_data)

    task_data.to_do_morning = data.get(
        "to_do_morning",
        []
    )

    task_data.to_do_afternoon = data.get(
        "to_do_afternoon",
        []
    )

    task_data.to_do_evening = data.get(
        "to_do_evening",
        []
    )

    task_data.in_progress = data.get(
        "in_progress",
        []
    )

    task_data.completed = data.get(
        "completed",
        []
    )

    db.session.commit()

    return jsonify({
        "success": True
    })

@taskplanner_bp.route(
    "/load_tasks",
    methods=["GET"]
)
@login_required
def load_tasks():

    task_data = Task.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if not task_data:

        return jsonify({
            "to_do_morning": [],
            "to_do_afternoon": [],
            "to_do_evening": [],
            "in_progress": [],
            "completed": []
        })

    return jsonify({

        "to_do_morning":
            task_data.to_do_morning,

        "to_do_afternoon":
            task_data.to_do_afternoon,

        "to_do_evening":
            task_data.to_do_evening,

        "in_progress":
            task_data.in_progress,

        "completed":
            task_data.completed
    })
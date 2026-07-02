from flask import Blueprint, redirect, url_for, request, jsonify, flash
from flask_login import current_user, login_required
from app.utils import render_platform_template
from app.services.lecture_service import generate_lecture_summary
from app.models.lectures import Lecture
from app.models import db

lecture_bp = Blueprint("lecture", __name__)

@lecture_bp.route("/lectures/upload_media", methods=["GET", "POST"])
@login_required
def upload_media():
    if request.method == "POST":
        lecture_pdf = request.files.get("lecture_pdf")
        notes_pdf = request.files.get("notes_pdf")
        audio = request.files.get("audio_file")
        youtube = request.form.get("youtube_url", "").strip()

        lecture_uploaded = lecture_pdf and lecture_pdf.filename
        notes_uploaded = notes_pdf and notes_pdf.filename
        audio_uploaded = audio and audio.filename

        if lecture_uploaded or notes_uploaded or audio_uploaded or youtube:
            summary_result = generate_lecture_summary(
                pdf_file=lecture_pdf if lecture_uploaded else None,
                user_notes=notes_pdf if notes_uploaded else None,
                audio=audio if audio_uploaded else None,
                youtube_url=youtube if youtube else None
            )
            
            new_lecture = Lecture(lecture_summary=summary_result, user_id=current_user.user_id)

            db.session.add(new_lecture)
            db.session.commit()

            # FIX: Send the dynamic parameter so the template knows what to fetch
            return redirect(url_for("lecture.lecture_summary", lecture_id=new_lecture.lecture_id))

        flash("Please upload at least one PDF, an MP3, or provide a YouTube URL.", "error")
        return redirect(url_for("lecture.upload_media"))

    return render_platform_template("upload_media.html")

@lecture_bp.route("/lectures/lecture_summary", methods=["GET"])
@login_required
def lecture_summary():
    lecture_id = request.args.get("lecture_id")
    lecture = Lecture.query.filter_by(lecture_id=lecture_id, user_id=current_user.user_id).first_or_404()
    return render_platform_template("lecture_summary.html", lecture=lecture)
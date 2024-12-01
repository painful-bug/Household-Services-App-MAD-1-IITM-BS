from flask import Blueprint, redirect, request, url_for
from flask_login import login_required
from App.models.db_models import User, Professional, db

users = Blueprint('users', __name__, url_prefix="/users")

@users.route("/block/<int:id>", methods=["POST"])
@login_required
def block_user(id):
  reason_for_block = request.form.get("block_reason")
  user_to_be_blocked = User.query.filter_by(
    id=id
  ).first()
  user_to_be_blocked.is_blocked = True
  user_to_be_blocked.is_active = False
  user_to_be_blocked.block_reason = reason_for_block
  print("block reasons : ",reason_for_block)
  print("is active : ", user_to_be_blocked.is_active)
  print("is blocked : ", user_to_be_blocked.is_blocked)
  db.session.commit()
  user_after_being_blocked = User.query.filter_by(
    id=id
  ).first()
  if user_after_being_blocked.is_blocked:
    print(f"{user_after_being_blocked.first_name} has been blocked!")
  else:
    print(f"{user_after_being_blocked.first_name} has NOT been blocked!")

  return redirect(url_for('admin.admin_dashboard'))


@users.route("/unblock/<int:id>", methods=["POST"])
@login_required
def unblock_user(id):
  user_to_be_unblocked = User.query.filter_by(
    id=id
  ).first()
  user_to_be_unblocked.is_blocked = False
  user_to_be_unblocked.is_active = True

  print("is active : ", user_to_be_unblocked.is_active)
  print("is blocked : ", user_to_be_unblocked.is_blocked)
  db.session.commit()
  user_after_being_unblocked = User.query.filter_by(
    id=id
  ).first()
  if user_after_being_unblocked.is_active:
    print(f"{user_after_being_unblocked.first_name} has been unblocked!")
  else:
    print(f"{user_after_being_unblocked.first_name} has NOT been unblocked!")

  return redirect(url_for('admin.admin_dashboard'))
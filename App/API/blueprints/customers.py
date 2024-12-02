from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_required
from App.models.db_models import User, ServiceRequest, db
from flask_login import current_user

customers = Blueprint('customers', __name__, url_prefix="/customers")

@customers.route("/past-requests")
@login_required
def past_requests():
  print("CURRENT USER CUSTOMER ID : ", current_user.customer_profile.id)
  past_requests = ServiceRequest.query.filter(
    ServiceRequest.customer_id == current_user.customer_profile.id,
    # ServiceRequest.status == "completed",
    # ServiceRequest.status == "rejected"
  ).all()
  print(f"PAST REQUESTS OF {current_user.first_name} : ", past_requests)
  return render_template("past-requests.html", past_requests=past_requests,user=current_user)
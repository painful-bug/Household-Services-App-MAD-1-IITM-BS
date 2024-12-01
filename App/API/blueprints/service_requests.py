from flask import Blueprint, redirect, request, url_for, jsonify, render_template, flash
from flask_login import login_required, current_user
from App.models.db_models import db, Professional, Service, ServiceRequest, Customer, Review
from datetime import datetime

service_requests = Blueprint('service_requests', __name__, url_prefix="/service-requests")

@service_requests.route("/select/<int:service_id>", methods=["POST"])
@login_required
def select_service_professional(service_id):

    print("SERVICE ID : ", service_id)
    service = Service.query.get(service_id)
    print("SERVICE : ", service)
    professionals = Professional.query.filter(
        Professional.service_id == service_id,
        Professional.is_available == True,
        Professional.is_verified == True
        ).all()
    print(f"PROFESSIONALS FIT FOR {service} : ", professionals)
    return render_template("list-of-professionals.html", 
                         service=service, 
                         professionals=professionals,
                         user=current_user)

@service_requests.route("/create/", methods=["POST"])
@login_required
def create_service_request():
    service_id = request.form.get('service-id')
    professional_id = request.form.get('professional-id')
    preferred_date = request.form.get('preferred-date')
    

    customer = Customer.query.filter_by(user_id=current_user.id).first()
    prof = Professional.query.filter_by(id=professional_id).first()
    prof.is_available = False
    # Creating a service request
    service_request = ServiceRequest(
        service_id=service_id,
        customer_id=customer.id,
        professional_id=professional_id,
        preferred_date=datetime.strptime(preferred_date, '%Y-%m-%d'),
        status='pending'
    )
    
    try:
        db.session.add(service_request)
        db.session.add(prof)
        db.session.commit()
        flash('Service request created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating service request!', 'danger')
        
    return redirect(url_for('auth.customer_dashboard'))

@service_requests.route("/update-status/<int:request_id>", methods=["POST"])
@login_required
def update_request_status(request_id):
    new_status = request.form.get('status')
    print("NEW STATUS : ", new_status)
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if new_status:
        if current_user.professional_profile.id != service_request.professional_id:
            flash('Unauthorized action!', 'danger')
            return redirect(url_for('auth.professional_dashboard'))
        else:
            current_prof = Professional.query.filter_by(id=current_user.professional_profile.id).first()
            if new_status == "accepted":
                current_prof.is_available = False
            if new_status == "completed" or new_status == "rejected" or new_status == "cancelled":
                current_prof.is_available = True

    service_request.status = new_status
    # db.session.add(service_request)
    # db.session.add(current_prof)
    db.session.commit()
    flash(f'Request {new_status} successfully!', 'success')
    return redirect(url_for('auth.professional_dashboard'))

@service_requests.route("/update-customer-status/<int:request_id>", methods=["POST"])
@login_required
def update_customer_request_status(request_id):
    new_status = request.form.get('status')
    new_date = request.form.get("new-date")
    print("NEW DATE : ", new_date)
    service_request = ServiceRequest.query.get_or_404(request_id)
    curr_prof = Professional.query.filter_by(id = service_request.professional_id).first()
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    if customer.id != service_request.customer_id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('auth.customer_dashboard'))
    if new_date:
        new_date = datetime.strptime(new_date, '%Y-%m-%d')
        service_request.preferred_date = new_date
    if new_status:
        service_request.status = new_status
    if new_status == 'completed':
        service_request.date_of_completion = datetime.now()
        curr_prof.is_available = True
        # db.session.add(service_request)
        # db.session.add(curr_prof)
        flash(f'Request marked as {new_status}!', 'success')
    db.session.commit()
    
    if new_status == 'completed':
        return redirect(url_for('service_requests.add_review', request_id=request_id))
    return redirect(url_for('auth.customer_dashboard'))

@service_requests.route("/add-review/<int:request_id>", methods=["GET", "POST"])
@login_required
def add_review(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if request.method == "POST":
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        review = Review(
            service_request_id=request_id,
            customer_id=service_request.customer_id,
            professional_id=service_request.professional_id,
            rating=rating,
            comment=comment
        )
        
        # Updating professional's average rating
        professional = Professional.query.get(service_request.professional_id)
        total_reviews = len(professional.reviews)
        # THIS FORMULA CAN ALSO BE APPLIED HERE : New average = old average * (n-1)/n + new value /n
        new_rating = ((professional.rating * total_reviews) + float(rating)) / (total_reviews + 1)
        professional.rating = round(new_rating, 1)
        
        db.session.add(review)
        db.session.commit()
        flash('Thank you for your review!', 'success')
        return redirect(url_for('auth.customer_dashboard'))
    
    return render_template('add-review.html', 
                         service_request=service_request,
                         user=current_user)
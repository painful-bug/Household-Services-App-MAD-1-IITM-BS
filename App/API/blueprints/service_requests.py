from flask import Blueprint, redirect, request, url_for, jsonify, render_template, flash
from flask_login import login_required, current_user
from App.models.db_models import db, Professional, Service, ServiceRequest, Customer, Review
from datetime import datetime
from App.API.blueprints.auth import auth

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
    current_service_requests = ServiceRequest.query.all() 
    print(f"PROFESSIONALS FIT FOR {service} : ", professionals)
    return render_template("list-of-professionals.html", 
                         service=service, 
                         professionals=professionals,
                         user=current_user,
                         current_service_requests=current_service_requests)

@service_requests.route("/create/", methods=["POST"])
@login_required
def create_service_request():
    service_id = request.form.get('service-id')
    professional_id = request.form.get('professional-id')
    preferred_date = request.form.get('preferred-date')
    preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d')
    
    # Check if professional has any accepted requests on the preferred date
    requested_prof = Professional.query.filter_by(id=professional_id).first()
    existing_request = ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='accepted',
        preferred_date=preferred_date_obj
    ).first()
    existing_pending_request = ServiceRequest.query.filter_by(
        professional_id=professional_id,
        customer_id=current_user.id,
        status='pending',
        preferred_date=preferred_date_obj
    ).first()
    existing_pending_requests_from_other_users = ServiceRequest.query.filter_by(
        professional_id=professional_id,
        status='pending',
        preferred_date=preferred_date_obj
    ).all()
    if existing_pending_requests_from_other_users:
        for i in existing_pending_requests_from_other_users:
            if i.customer_id != current_user.id:
                # i.status = "cancelled"
                i.prof_busy_on_same_day = True  
            db.session.add(i)
    if existing_request:
        flash('This professional is already booked for the selected date. Please choose another date or professional.', 'warning')
        return redirect(url_for('auth.customer_dashboard'))
    if existing_pending_request:
        flash('You have already selected this professional for a service. Please wait for the professional to approve or reject your request before making another service request', 'warning')
        return redirect(url_for('auth.customer_dashboard'))
    
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    
    # Creating a service request
    service_request = ServiceRequest(
        service_id=service_id,
        customer_id=customer.id,
        professional_id=professional_id,
        preferred_date=preferred_date_obj,
        status='pending'
    )
    
    try:
        db.session.add(service_request)
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
            if new_status == "completed" or new_status == "rejected" or new_status == "cancelled":
                current_prof.is_available = True

    service_request.status = new_status
    db.session.add(service_request)
    db.session.add(current_prof)
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
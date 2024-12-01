from io import BytesIO
from flask import Blueprint, jsonify, redirect, render_template, url_for, request, flash, current_app, send_file
from flask_login import current_user, login_required
from App.models.db_models import User, Service, Professional, Docs, ServiceRequest, Review
from App import db
from werkzeug.utils import secure_filename
import os
from sqlalchemy.exc import SQLAlchemyError
import logging

admin = Blueprint('admin', __name__, url_prefix="/admin")
UPLOADED_DOCS = 'static/uploaded_docs'

@admin.route("/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    pending_professionals = User.query.join(Professional).filter(
        User.role == "professional",
        Professional.document_verification_status == "pending"
    ).all()
    # pending_professionals = Professional.query.filter(Professional.document_verification_status == "pending").all()
    print('PENDING PROFESSIONALS : ',pending_professionals)
    services = Service.query.all()
    
    return render_template('admin-dashboard.html', 
                         admin=current_user,
                         users=users, 
                         pending_professionals=pending_professionals,
                         services=services)

@admin.route("/delete_user/<int:id>", methods=["GET","POST"])
@login_required
def delete_user(id):
    if current_user.role != "admin":
        return redirect(url_for('main.index'))
    
    try:
        # Disable autoflush temporarily
        with db.session.no_autoflush:
            user_to_be_deleted = User.query.get_or_404(id)
            professional = Professional.query.filter_by(user_id=id).first()
            
            if professional:
                docs = Docs.query.filter_by(professional_id=professional.id).first()
                reviews = Review.query.filter_by(professional_id=professional.id).all()
                service_requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
        
                if docs:
                    db.session.delete(docs)

                for review in reviews:
                    db.session.delete(review)

                for service_request in service_requests:
                    db.session.delete(service_request)
                
                db.session.flush()
                
                db.session.delete(professional)
                db.session.flush()
            
            if user_to_be_deleted.role == "customer":
                reviews_customer = Review.query.filter_by(customer_id = user_to_be_deleted.id).all()
                service_requests_customer = ServiceRequest.query.filter_by(customer_id = user_to_be_deleted.id).all()
                db.session.delete(reviews_customer)
                db.session.delete(service_requests_customer)
                db.session.flush()
         
            db.session.delete(user_to_be_deleted)
            db.session.commit()
            
        flash("User has been deleted", "success")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error deleting user: {str(e)}")
        flash("An error occurred while deleting the user. Please try again.", "error")
    finally:
        db.session.close()
    
    return redirect(url_for('admin.admin_dashboard'))



    

@admin.route("/get-professional-docs/<int:user_id>")
@login_required
def get_professional_docs(user_id):
    if current_user.role != "admin":
        return redirect(url_for('main.index'))
    print("USER ID ON WHICH DOCS IS TO BE SEARCHED : ", user_id)
    prof_id = Professional.query.filter_by(user_id=user_id).first().id
    print("PROFESSIONAL ID ON WHICH DOCS IS TO BE SEARCHED : ", prof_id)
    docs = Docs.query.filter_by(professional_id=prof_id).first()
    print("DOCS : ",docs)
    if docs:
        return send_file(
            BytesIO(docs.data),
            download_name=docs.filename,
            as_attachment=False,
            mimetype='application/pdf'
        )
    else:
        return jsonify("failed to retrieve document. Please go back.")

@admin.route("/service/create", methods=["POST"])
@login_required
def create_service():
    if current_user.role != "admin":
        return redirect(url_for('main.index'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    base_price = float(request.form.get('base_price'))
    time_required = request.form.get('time_required')
    
    service = Service(
        name=name,
        base_price=base_price,
        description=description,
        time_required=time_required
    )
    
    try:
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating service!', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin.route("/service/<int:service_id>/update", methods=["POST"])
@login_required
def update_service(service_id):
    if current_user.role != "admin":
        return redirect(url_for('main.index'))
    
    service = Service.query.get_or_404(service_id)
    service.name = request.form.get('name')
    service.description = request.form.get('description')
    service.base_price = float(request.form.get('base_price'))
    service.time_required = request.form.get('time_required')
    
    try:
        db.session.commit()
        flash('Service updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating service!', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin.route("/service/<int:service_id>/delete")
@login_required
def delete_service(service_id):
    if current_user.role != "admin":
        return redirect(url_for('main.index'))
    
    service = Service.query.get_or_404(service_id)
    
    try:
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting service!', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))

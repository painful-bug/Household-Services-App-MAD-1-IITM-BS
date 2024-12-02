from flask import Blueprint, flash, redirect, request, url_for, render_template, jsonify
from flask_login import login_required
from App.models.db_models import ServiceRequest, User, Professional, Docs, Review, db

professionals = Blueprint('professionals', __name__,
                          url_prefix="/professionals")


@professionals.route("/view-docs/<int:id>", methods=["POST"])
@login_required
def view_docs(id):
    if request.method == "POST":
        professional = Professional.query.get_or_404(id)
        professional_docs_thru_user = Docs.query.filter_by(
            professional_id=professional.id).first()
        professional_docs = Docs.query.filter_by(professional_id=id).first()
        if professional_docs_thru_user:
            return render_template('admin-dashboard.html',
                    professional_docs=professional_docs_thru_user,
                    users=User.query.all(),
                    pending_professionals=Professional.query.all())

        if professional_docs:
            return render_template('admin-dashboard.html', 
                                professional_docs=professional_docs,
                                users=User.query.all(),
                                pending_professionals=Professional.query.all())
        else:
            flash("No documents found for this professional", "warning")
            return redirect(url_for('admin.admin_dashboard'))

@professionals.route("/approve/<int:id_>", methods=["POST"])
def approve_professional(id_):
  if request.method == "POST":
    req_prof = Professional.query.filter_by(user_id=id_).first()
    if req_prof:
      print("REQUESTED PROFESSIONAL TO BE APPROVED : ", req_prof)
      req_prof.is_verified = True
      req_prof.document_verification_status = "approved"
      db.session.add(req_prof)
      db.session.commit()
      flash(f"Approved {User.query.filter_by(id=id_).first().first_name}", "success")
    else:
       flash("Professional not found!", "success")
    return redirect(url_for('admin.admin_dashboard'))

@professionals.route("/reject/<int:id_>", methods=["POST"])
def reject_professional(id_):
    if request.method == "POST":
        professional = Professional.query.filter_by(user_id=id_).first()
        if professional:
            reject_reason = request.form.get('reject_reason')
            professional.document_verification_status = "rejected"
            professional.rejection_reason = reject_reason
            db.session.commit()
            flash(f"Professional rejected. Reason: {reject_reason}", "warning")
        else:
            flash("Professional not found!", "error")
        return redirect(url_for('admin.admin_dashboard'))

@professionals.route("/view-profile/<int:id>")
@login_required
def view_profile(id):
    # Get the user and their professional profile
    user = User.query.get_or_404(id)
    professional = Professional.query.filter_by(user_id=id).first()
    
    if not professional:
        return jsonify({'error': 'Professional profile not found'}), 404
    
    response_data = {
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        },
        'professional': {
            'experience_years': professional.experience_years,
            'location_pincode': professional.location_pincode,
            'preferred_service': professional.preferred_service,
            'rating': professional.rating,
            'description': professional.description,
            'verification_status': 'Verified' if professional.is_verified else 'Pending',
            'is_verified': professional.is_verified
        }
    }
    
    return jsonify(response_data)

@professionals.route("/add-description/<int:id>", methods=["GET","POST"])
@login_required
def add_description(id):
   if request.method == "POST":
    desc = request.form.get("desc")
    print("DESCRIPTION GOT : ", desc)
    req_prof_for_descr = Professional.query.filter_by(id=id).first()
    print("REQ PROF FOR DESCR : ", req_prof_for_descr)
    req_prof_for_descr.description = desc
    db.session.add(req_prof_for_descr)
    db.session.commit()
    # flash("Description Updated!", "success")
    return redirect(url_for("auth.professional_dashboard"))

@professionals.route("/reupload-docs/<int:user_id>", methods=["POST"])
@login_required
def reupload_docs(user_id):
    if request.method == "POST":
        professional = Professional.query.filter_by(user_id=user_id).first()
        
        if not professional:
            flash("Professional profile not found", "error")
            return redirect(url_for('auth.professional_dashboard'))
        
        if 'document' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('auth.professional_dashboard'))
            
        file = request.files['document']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('auth.professional_dashboard'))
            
        if file:
            existing_docs = Docs.query.filter_by(professional_id=professional.id).first()
            if existing_docs:
                db.session.delete(existing_docs)
                
            new_docs = Docs(
                professional_id=professional.id,
                filename=file.filename,
                data=file.read()
            )
            
            professional.document_verification_status = "pending"
            
            db.session.add(new_docs)
            db.session.commit()
            
            # flash("Documents uploaded successfully. Waiting for admin approval.", "success")
            return redirect(url_for('auth.professional_dashboard'))
            
        flash("Error uploading documents", "error")
        return redirect(url_for('auth.professional_dashboard'))


@professionals.route("/get-rating-data/<int:id>", methods=["GET","POST"])
def get_rating_data(id):
    ratings = Review.query.filter(
        Review.professional_id == id
    ).all()
    ratings_values = []
    for i in ratings:
        ratings_values.append(i.rating)
    print(ratings_values)
    return jsonify(ratings_values)

@professionals.route("/get-accepted-rejected-data/<int:id>", methods=["GET","POST"])
def get_accepted_rejected_sr_data(id):
    service_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == id
    ).all()

    accepted_count = rejected_count = 0
    for req in service_requests:
        print("REQ ID : ",req.id)
        if req.status == "completed":
            accepted_count = accepted_count + 1
        if req.status == "rejected":
            rejected_count = rejected_count + 1
    print("COMPLETED COUNT : ", accepted_count)
    print("REJECTED COUNT : ", rejected_count)
    return jsonify({
        "accepted_count" : accepted_count,
        "rejected_count": rejected_count
    })
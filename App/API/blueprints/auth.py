from flask import Blueprint, request, redirect, jsonify, render_template, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import JSON
from App.models.db_models import User, Customer, Professional, Service, ServiceRequest, Docs
from App import db
from email_validator import EmailNotValidError, validate_email
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__, url_prefix="/auth")

# VALID_ROLES = ['customer', 'admin', "professional"]  # Add all your valid roles here
# VALID_ROLES = [UserRole.CUSTOMER, UserRole.ADMIN, UserRole.PROFESSIONAL]


def process_form_data_signup(form_data: JSON) -> JSON:

    if "first_name" in form_data and "last_name" in form_data and "email" in form_data and "password" in form_data and "role" in form_data:
        first_name = form_data.get("first_name")
        middle_name = form_data.get("middle_name")
        last_name = form_data.get("last_name")
        email = form_data.get("email")
        password = form_data.get("password")
        role = form_data.get("role")
    print("CURRENT ROLE : ", role)
    # Email Validation
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        return "bad email"

    return {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role": role
    }


def process_form_data_login(form_data: JSON) -> JSON:
    email = form_data.get("email")
    password = form_data.get("password")
    # Email Validation
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        return "bad email"


    return {
        "email": email,
        "password": password
    }



@auth.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        form_data = request.form
        user_data = process_form_data_signup(form_data)
        print("User data received from form : ", user_data)
        if "bad email" in user_data:
            flash("Email is not valid! Please enter a correct email address.", "danger")
            return redirect(url_for('auth.signup'))


        user = User.query.filter_by(email=str(user_data["email"])).first()
        if user is not None:
            flash("User already exists! Please proceed to login!", "warning")
            return redirect(url_for('auth.login'))

        # Create new user
        new_user = User(
            first_name=user_data["first_name"],
            middle_name=user_data["middle_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            password=user_data["password"],
            role=user_data["role"]
        )
        db.session.add(new_user)
        db.session.flush()  

        # Create role-specific profile

        if user_data["role"] == "customer":
            customer = Customer(
                user_id=new_user.id,
                phone=form_data.get("phone"),
                address=form_data.get("address"),
                location_pincode=form_data.get("pincode")
            )
            db.session.add(customer)
        elif user_data["role"] == "professional":
            preferred_service = Service.query.filter_by(name=form_data.get("preferred-service")).first()
            print("PREFERRED SERVICE FROM SIGNUP: ", preferred_service)
            preferred_service_id = preferred_service.id
            print("PREFERRED SERVICE ID FROM SIGNUP: ", preferred_service_id)
            professional = Professional(
                user_id=new_user.id,
                experience_years=int(form_data.get("experience", 0)),
                description=form_data.get("description"),
                location_pincode=form_data.get("pincode"),
                document_verification_status="pending",
                preferred_service=preferred_service.name,
                service_id=preferred_service_id
            )
            db.session.add(professional)
            db.session.flush()  
            
            file = request.files["docs"]
            if file:
                uploaded_docs = Docs(
                    professional_id=professional.id,  
                    filename=secure_filename(file.filename),
                    data=file.read()
                )
                db.session.add(uploaded_docs)
            
            db.session.commit()
            flash(f"File with filename : {file.filename} has been uploaded!", "success")

        db.session.commit()

        login_user(new_user)
        flash(f"Welcome, {
              new_user.first_name}! Your account has been created.", "success")
        return redirect(url_for('auth.login'))
    all_available_services = Service.query.all()
    return render_template("signup.html", services=all_available_services)


@auth.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        form_data = request.form
        user_data = process_form_data_login(form_data)

        if "bad email" in user_data:
            flash("Email is not valid! Please enter a correct email address.", "danger")
            return redirect(url_for('auth.login'))
        try:
            user = User.query.filter_by(email=str(user_data["email"])).first()
            # - TODO : WILL ALLOW USER TO LOGIN AND THEN DISPLAY A MESSAGE THAT HE/SHE IS BLOCKED BY ADMIN, AND THEY CAN SEND ADMIN AN EMAIL (EMAIL ADDRESS OF ADMIN WILL BE VISIBLE). THE BLOCKED USER WILL ALSO BE ABLE TO SEE THE REASON HE IS BLOCKED BY THE ADMIN.
            if user.is_blocked:
                flash("User is blocked by the admin and cannot log in", "danger")
                return redirect(url_for('auth.login'))

            if user and user.verify_password(user_data["password"]):
                login_user(user)
                flash(f"Welcome back, {user.first_name}!", "success")
                print("CURRENT USER : ", user)
                # Redirect based on role
                if user.role == "admin":
                    return redirect(url_for('admin.admin_dashboard'))
                elif user.role == "professional":
                    return redirect(url_for('auth.professional_dashboard'))
                else:  # Customer
                    return redirect(url_for('auth.customer_dashboard'))
            else:
                flash("Incorrect email or password", "danger")
                return redirect(url_for('auth.login'))
        except Exception as e:
            print("ERROR : ", str(e))
            flash("An error occurred during login", "danger")
            return redirect(url_for('auth.login'))

    return render_template("login.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()

    return render_template("login.html")


@auth.route("/professional-dashboard")
@login_required
def professional_dashboard():
    if current_user.role != "professional":
        flash("Access denied. Professional account required.", "danger")
        return redirect(url_for('auth.login'))
    
    current_professional_user = Professional.query.filter_by(
        user_id=current_user.id
    ).first()
    
    service_requests = ServiceRequest.query.filter(
        ServiceRequest.professional_id == current_professional_user.id
    ).all()

    accepted_count = rejected_count = 0
    for req in service_requests:
        if req.status == "accepted":
            accepted_count = accepted_count + 1
        if req.status == "rejected":
            rejected_count = rejected_count + 1
    
    return render_template("service-professional.html", user=current_user, professional=current_professional_user,)


@auth.route("/customer-dashboard")
@login_required
def customer_dashboard():
    if current_user.role != "customer":
        flash("Access denied. Customer account required.", "danger")
        return redirect(url_for('auth.login'))
    # TODO add the ability to check whether all the professionals who has a certain preferred service is unavailable. If so, make that service inactive
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    services = Service.query.filter(
        Service.is_active == True
    ).all()
    service_requests = ServiceRequest.query.filter_by(
        customer_id=customer.id).all()
    if current_user.is_blocked:
        pass
    return render_template("customer-dashboard.html",
                           user=current_user,
                           services=services,
                           service_requests=service_requests)


@auth.route("/delete-user/<int:id>", methods=["GET"])
def delete_user(id):
    user = User.query.get_or_404(id) 
    print("ID : ", id)
    try:
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {id} successfully deleted"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to delete user"}, 500


from flask import redirect, render_template, url_for
from flask_login import LoginManager, current_user
from App import create_app
from App.API.blueprints.professionals import professionals
from App.API.blueprints.services import services
from App.API.blueprints.admin import admin
from App.API.blueprints.auth import auth
from App.API.blueprints.users import users
from App.API.blueprints.customers import customers
from App.API.blueprints.service_requests import service_requests
from App.models.db_models import User

app = create_app()

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        """
        if the user is authenticated, redirect to their respective dashboard in accordance with their roles
        """
        print("CURRENT USER FROM APP.PY : ", current_user.role)
        if current_user.role == "admin":
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == "professional":
            return redirect(url_for('auth.professional_dashboard'))
        else: 
            return redirect(url_for('auth.customer_dashboard'))  
    else:
        return redirect(url_for('auth.login'))


with app.app_context():
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(users)
    app.register_blueprint(customers)
    app.register_blueprint(services)
    app.register_blueprint(service_requests)
    app.register_blueprint(professionals)
if __name__ == "__main__":
    app.run(debug=True)

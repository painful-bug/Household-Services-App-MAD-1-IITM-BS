from flask import Blueprint, redirect, request, url_for
from flask_login import login_required
from App.models.db_models import User, db

customers = Blueprint('customers', __name__, url_prefix="/customers")


from flask import Blueprint, redirect, request, url_for, jsonify
from flask_login import login_required
from App.models.db_models import db, Service, Professional

services = Blueprint('services', __name__, url_prefix="/services")


@services.route("/search/<string:q>", methods=["POST", "GET"])
@login_required
def search_services(q: str):
    if q.isnumeric():
        requested_profs = Professional.query.filter(
            Professional.location_pincode.ilike(f"%{q}%")).all()
        requested_services = []
        for prof in requested_profs:
            requested_services.append(Service.query.filter_by(id=prof.service_id).first())
        requested_services = list(set(requested_services))
    else:
        requested_services = Service.query.filter(
                Service.name.ilike(f"%{q}%")).all()
    services_list = [
        {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required,
            'is_active': service.is_active,
            'created_at': service.created_at,
            'updated_at': service.updated_at,
        }
        for service in requested_services
    ]
    print("REQUESTED SERVICES : ", services_list)
    return jsonify(services_list)


@services.route("/search/", methods=["POST", "GET"])
@login_required
def get_services():

    requested_services = Service.query.all()

    services_list = [
        {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': service.base_price,
            'time_required': service.time_required,
            'is_active': service.is_active,
            'created_at': service.created_at,
            'updated_at': service.updated_at,
        }
        for service in requested_services
    ]
    print("REQUESTED SERVICES : ", services_list)
    return jsonify(services_list)

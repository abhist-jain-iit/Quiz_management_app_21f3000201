from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.tasks import export_user_csv, export_admin_csv
from app.auth import admin_required

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/export/user-csv', methods=['POST'])
@jwt_required()
def export_user_csv_endpoint():
    user_id = get_jwt_identity()
    export_user_csv.delay(user_id)
    return jsonify({'message': 'Your CSV export has been started. You will be notified when it is ready.'}), 202

@export_bp.route('/api/export/admin-csv', methods=['POST'])
@jwt_required()
@admin_required()
def export_admin_csv_endpoint():
    export_admin_csv.delay()
    return jsonify({'message': 'Admin CSV export has been started. You will be notified when it is ready.'}), 202 
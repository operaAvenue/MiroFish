"""
Admin API for Oracle Jurídico.
Handles user management, Mercado Pago configuration, system settings, and PageBuilder assets.
"""

import os
import json
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from ..services.auth_service import AuthService
from .auth import admin_required
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('oracle.api.admin')
admin_bp = Blueprint('admin', __name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# ================= User Management =================
@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Lists all registered users."""
    auth_service = AuthService.get_instance()
    users = auth_service.list_users()
    return jsonify({
        "success": True,
        "data": users
    })

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Updates a user's status or role."""
    data = request.get_json() or {}
    auth_service = AuthService.get_instance()
    
    if 'status' in data:
        valid_statuses = {'active', 'pending_payment', 'blocked'}
        if data['status'] not in valid_statuses:
            return jsonify({"success": False, "error": f"Status inválido: {data['status']}"}), 400
        auth_service.update_user_status(user_id, data['status'])
        
    if 'role' in data:
        valid_roles = {'admin', 'user'}
        if data['role'] not in valid_roles:
            return jsonify({"success": False, "error": f"Perfil inválido: {data['role']}"}), 400
        auth_service.update_user_role(user_id, data['role'])

    updated_user = auth_service.get_user_by_id(user_id)
    return jsonify({
        "success": True,
        "data": updated_user
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Deletes a user."""
    auth_service = AuthService.get_instance()
    success = auth_service.delete_user(user_id)
    if not success:
        return jsonify({"success": False, "error": "Usuário não encontrado."}), 404
    return jsonify({"success": True, "message": "Usuário excluído com sucesso."})

# ================= Settings & PageBuilder =================
@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    """Retrieves all settings."""
    auth_service = AuthService.get_instance()
    settings = auth_service.get_all_settings()
    return jsonify({
        "success": True,
        "data": settings
    })

@admin_bp.route('/settings', methods=['POST'])
@admin_required
def update_settings():
    """Updates settings (Mercado Pago, Google, PageBuilder)."""
    data = request.get_json() or {}
    auth_service = AuthService.get_instance()

    allowed_keys = {
        'admin_email',
        'google_client_id',
        'google_client_secret',
        'mp_access_token',
        'mp_public_key',
        'mp_webhook_secret',
        'mp_plan_title',
        'mp_plan_price',
        'mp_plan_currency',
        'homepage_config'
    }

    for key, val in data.items():
        if key in allowed_keys:
            if key == 'homepage_config' and isinstance(val, (dict, list)):
                val_str = json.dumps(val, ensure_ascii=False)
            else:
                val_str = str(val)
            auth_service.set_setting(key, val_str)

    logger.info("Admin updated system settings")
    return jsonify({
        "success": True,
        "message": "Configurações salvas com sucesso.",
        "data": auth_service.get_all_settings()
    })

# ================= Asset Upload (PageBuilder) =================
@admin_bp.route('/upload', methods=['POST'])
@admin_required
def upload_asset():
    """Uploads a logo or hero image asset."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Nome de arquivo vazio."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Formato de arquivo não suportado (apenas imagens)."}), 400

    branding_dir = os.path.join(Config.UPLOAD_FOLDER, 'branding')
    os.makedirs(branding_dir, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex[:12]}.{ext}"
    target_path = os.path.join(branding_dir, unique_name)
    file.save(target_path)

    asset_url = f"/api/admin/branding/{unique_name}"
    logger.info(f"Asset uploaded: {unique_name}")

    return jsonify({
        "success": True,
        "url": asset_url,
        "filename": unique_name
    })

@admin_bp.route('/branding/<filename>', methods=['GET'])
def serve_branding(filename):
    """Serves uploaded branding images publicly."""
    branding_dir = os.path.join(Config.UPLOAD_FOLDER, 'branding')
    return send_from_directory(branding_dir, filename)

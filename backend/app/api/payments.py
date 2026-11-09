"""
Payments API for Oracle Jurídico.
Handles Mercado Pago Checkout Pro preferences and Webhook processing.
"""

from flask import Blueprint, request, jsonify
import requests

from ..services.auth_service import AuthService
from .auth import login_required, get_current_user
from ..utils.logger import get_logger

logger = get_logger('oracle.api.payments')
payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/mercadopago/preference', methods=['POST'])
@login_required
def create_preference():
    """Creates a Mercado Pago checkout preference for the current user."""
    user = get_current_user()
    auth_service = AuthService.get_instance()

    mp_access_token = auth_service.get_setting("mp_access_token")
    if not mp_access_token:
        return jsonify({
            "success": False,
            "error": "Integração do Mercado Pago ainda não foi configurada pelo administrador."
        }), 400

    plan_title = auth_service.get_setting("mp_plan_title", "Assinatura Anual Oracle Jurídico")
    try:
        plan_price = float(auth_service.get_setting("mp_plan_price", "197.00"))
    except ValueError:
        plan_price = 197.00
    plan_currency = auth_service.get_setting("mp_plan_currency", "BRL")

    payload = {
        "items": [
            {
                "title": plan_title,
                "quantity": 1,
                "currency_id": plan_currency,
                "unit_price": plan_price,
                "description": "Acesso completo à plataforma Oracle Jurídico"
            }
        ],
        "payer": {
            "email": user["email"],
            "name": user.get("name") or user["email"]
        },
        "external_reference": str(user["id"]),
        "back_urls": {
            "success": "https://oracle.fcsg.fr/?payment=success",
            "failure": "https://oracle.fcsg.fr/checkout?payment=failure",
            "pending": "https://oracle.fcsg.fr/checkout?payment=pending"
        },
        "auto_return": "approved",
        "notification_url": "https://oracle.fcsg.fr/api/payments/mercadopago/webhook"
    }

    try:
        resp = requests.post(
            "https://api.mercadopago.com/checkout/preferences",
            json=payload,
            headers={
                "Authorization": f"Bearer {mp_access_token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if resp.status_code not in (200, 201):
            logger.error(f"Mercado Pago API error: {resp.text}")
            return jsonify({
                "success": False,
                "error": "Erro ao gerar preferência de pagamento no Mercado Pago."
            }), 502

        pref_data = resp.json()
        init_point = pref_data.get("init_point")
        sandbox_init_point = pref_data.get("sandbox_init_point")

        return jsonify({
            "success": True,
            "init_point": init_point,
            "sandbox_init_point": sandbox_init_point,
            "preference_id": pref_data.get("id")
        })
    except Exception as e:
        logger.error(f"Exception calling Mercado Pago: {e}")
        return jsonify({
            "success": False,
            "error": f"Erro de conexão com Mercado Pago: {str(e)}"
        }), 500

@payments_bp.route('/mercadopago/webhook', methods=['POST'])
def mercadopago_webhook():
    """Webhook listener for Mercado Pago payment notifications."""
    data = request.get_json(silent=True) or {}
    logger.info(f"Mercado Pago webhook received: {data}")

    payment_id = None
    if 'data' in data and 'id' in data['data']:
        payment_id = str(data['data']['id'])
    elif 'id' in data:
        payment_id = str(data['id'])
    elif request.args.get('id'):
        payment_id = str(request.args.get('id'))
    elif request.args.get('data.id'):
        payment_id = str(request.args.get('data.id'))

    action = data.get('action') or data.get('type') or request.args.get('topic') or request.args.get('type')

    if not payment_id:
        return jsonify({"status": "ignored", "reason": "No payment ID found"}), 200

    auth_service = AuthService.get_instance()
    mp_access_token = auth_service.get_setting("mp_access_token")
    if not mp_access_token:
        logger.warning("Mercado Pago access token not configured, cannot verify webhook.")
        return jsonify({"status": "error", "message": "Access token not set"}), 200

    try:
        resp = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {mp_access_token}"},
            timeout=10
        )

        if resp.status_code == 200:
            payment_info = resp.json()
            status = payment_info.get("status")
            external_reference = payment_info.get("external_reference")
            amount = float(payment_info.get("transaction_amount", 0.0))
            currency = payment_info.get("currency_id", "BRL")
            payment_method = payment_info.get("payment_method_id", "mercadopago")

            logger.info(f"Verified payment {payment_id}: status={status}, user={external_reference}")

            if external_reference:
                try:
                    user_id = int(external_reference)
                    auth_service.record_payment(
                        user_id=user_id,
                        payment_id=payment_id,
                        status=status,
                        amount=amount,
                        currency=currency,
                        payment_method=payment_method,
                        raw_data=str(payment_info)
                    )
                    logger.info(f"User {user_id} payment recorded. Status={status}")
                except ValueError:
                    logger.error(f"Invalid external_reference: {external_reference}")

    except Exception as e:
        logger.error(f"Error querying payment from Mercado Pago: {e}")

    return jsonify({"status": "received"}), 200

@payments_bp.route('/status', methods=['GET'])
@login_required
def payment_status():
    """Checks the payment/activation status of the current user."""
    user = get_current_user()
    return jsonify({
        "success": True,
        "status": user.get("status"),
        "role": user.get("role")
    })

"""
API路由模块
"""

from flask import Blueprint

graph_bp = Blueprint('graph', __name__)
simulation_bp = Blueprint('simulation', __name__)
report_bp = Blueprint('report', __name__)

from . import graph  # noqa: E402, F401
from . import simulation  # noqa: E402, F401
from . import report  # noqa: E402, F401
from .auth import auth_bp
from .admin import admin_bp
from .payments import payments_bp

__all__ = [
    'graph_bp',
    'simulation_bp',
    'report_bp',
    'auth_bp',
    'admin_bp',
    'payments_bp'
]

"""
API路由模块
"""

from .graph import graph_bp
from .simulation import simulation_bp
from .report import report_bp
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

# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, render_template
from flask_admin import Admin

from tegenaria import public, user
from tegenaria.assets import assets
from tegenaria.extensions import bcrypt, cache, db, debug_toolbar, login_manager, migrate
from tegenaria.models import Apartment, Pin
from tegenaria.settings import ProdConfig
from tegenaria.views import ApartmentModelView, PinModelView


def create_app(config_object=ProdConfig):
    """An application factory, as explained here.

    http://flask.pocoo.org/docs/patterns/appfactories/

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    """Register app extensions."""
    assets.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)

    # This extension doesn't behave like the others; that's why we had to initialise it here, not outside:
    # https://github.com/flask-admin/flask-admin/issues/910
    admin = Admin(name='Tegenaria', template_mode='bootstrap3')
    admin.init_app(app)
    admin.add_view(ApartmentModelView(Apartment, db.session))
    admin.add_view(PinModelView(Pin, db.session))
    return None


def register_blueprints(app):
    """Register routes (blueprints)."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """If a HTTPException, pull the `code` attribute; default to 500."""
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None

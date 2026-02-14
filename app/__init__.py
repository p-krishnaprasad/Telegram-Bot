from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register blueprints
    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    from app.routes.telegram_bot import telegram_bp
    app.register_blueprint(telegram_bp)

    from app.routes.summary import summary_bp
    app.register_blueprint(summary_bp)

    return app
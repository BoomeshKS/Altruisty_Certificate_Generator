from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from routes.completion_routes import completion_bp

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(completion_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

# 🔥 THIS LINE IS MANDATORY FOR GUNICORN
app = create_app()

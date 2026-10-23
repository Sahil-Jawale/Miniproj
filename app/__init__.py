import os
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template

# Change this line and push to see the pipeline redeploy the app.
MESSAGE = "Version 2 - deployed automatically with GitHub Actions"


def create_app():
    app = Flask(__name__)
    started_at = datetime.now(timezone.utc)

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            message=MESSAGE,
            commit=os.getenv("APP_VERSION", "local-dev"),
            container=socket.gethostname(),
            started_at=started_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        )

    @app.route("/health")
    def health():
        return jsonify(status="ok", version=os.getenv("APP_VERSION", "local-dev"))

    return app


app = create_app()

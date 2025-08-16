from flask import Flask, request, jsonify, render_template
import util
import os

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/get_location_names", methods=["GET"])
    def get_location_names():
        try:
            locations = util.get_location_names()
            return jsonify({"locations": locations}), 200
        except Exception as e:
            # Helps debug on the client
            return jsonify({"error": str(e)}), 500

    @app.route("/predict_home_price", methods=["POST"])
    def predict_home_price():
        try:
            data = request.get_json(force=True) if request.is_json else request.form
            total_sqft = float(data.get("total_sqft"))
            bhk = int(data.get("bhk"))
            bath = int(data.get("bath"))
            location = data.get("location") or data.get("loc") or ""

            est = util.get_estimated_price(location, total_sqft, bhk, bath)
            return jsonify({"estimated_price_lakh": round(float(est), 2)}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # Simple health endpoint
    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    return app

if __name__ == "__main__":
    # Enable reloader for local dev
    port = int(os.environ.get("PORT", 5000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)

from label_studio_ml.api import init_app
from garage_model import GarageModel

# Initialize the Label Studio ML app
app = init_app(GarageModel)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True, use_reloader=False)
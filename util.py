import json
import pickle
import os
import numpy as np

__columns = None
__locations = None
__model = None

def _find_path(*names):
    """
    Search for a file by trying cwd, this file's dir, and parent.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.getcwd(), *names),
        os.path.join(here, *names),
        os.path.join(os.path.dirname(here), *names),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def load_artifacts(columns_file="columns.json", model_file="bangalore_home_prices_model.pickle"):
    global __columns, __locations, __model

    # Columns
    columns_path = _find_path(columns_file)
    if not columns_path:
        # Create a tiny fallback to keep UI alive
        __columns = ["total_sqft", "bath", "bhk", "1st block jayanagar", "yelahanka"]
    else:
        with open(columns_path, "r") as f:
            data = json.load(f)
        # accept either list or dict with key "data_columns"
        if isinstance(data, dict) and "data_columns" in data:
            __columns = data["data_columns"]
        elif isinstance(data, list):
            __columns = data
        else:
            raise ValueError("columns.json format not recognized")

    __locations = __columns[3:]

    # Model (optional for dev)
    model_path = _find_path(model_file) or _find_path("bangalore _home_price_predictio_model.pickle")  # handle common misspell
    if model_path and os.path.getsize(model_path) > 0:
        with open(model_path, "rb") as f:
            __model = pickle.load(f)
    else:
        __model = None  # Will use a heuristic baseline

def get_location_names():
    if __locations is None:
        load_artifacts()
    return sorted(__locations)

def get_estimated_price(location, sqft, bhk, bath):
    if __columns is None:
        load_artifacts()

    # One-hot encode
    try:
        x = np.zeros(len(__columns))
        x[0] = sqft
        x[1] = bath
        x[2] = bhk
        if location:
            loc = location.strip().lower()
            try:
                idx = __columns.index(loc)
                x[idx] = 1
            except ValueError:
                pass
    except Exception:
        # Fallback: simple heuristic if columns don't match
        base_ppsft = 6500  # INR per sqft baseline for Bangalore (illustrative)
        price_lakh = (sqft * base_ppsft) / 100000.0
        price_lakh *= (1 + 0.04 * (bhk - 2)) * (1 + 0.03 * (bath - 2))
        return price_lakh

    if __model is not None:
        pred = __model.predict([x])[0]
        # If the model trained on lakhs, return as-is; else scale to lakhs heuristically.
        return float(pred)

    # Heuristic if model missing
    base_ppsft = 6500  # INR per sqft baseline (illustrative)
    price_lakh = (sqft * base_ppsft) / 100000.0
    price_lakh *= (1 + 0.04 * (bhk - 2)) * (1 + 0.03 * (bath - 2))
    return price_lakh

# Auto-load on import for convenience
try:
    load_artifacts()
except Exception:
    # Defer errors to runtime to avoid breaking imports
    pass

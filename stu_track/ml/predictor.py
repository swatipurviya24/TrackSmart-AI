# type: ignore

import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# MODEL AND LABEL PATHS
# ============================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ai_model",
    "behavior_model_v4.h5"
)

LABELS_PATH = os.path.join(
    BASE_DIR,
    "ai_model",
    "behavior_labels.json"
)


# ============================================================
# LOAD MODEL ONCE
# ============================================================

model = load_model(
    MODEL_PATH,
    compile=False
)


# ============================================================
# LOAD LABELS
# ============================================================

with open(LABELS_PATH, "r") as f:
    labels = json.load(f)


# ============================================================
# SETTINGS
# ============================================================

IMG_SIZE = (224, 224)

MOBILE_INDEX = 3

MOBILE_THRESHOLD = 0.42


# ============================================================
# PREDICT BEHAVIOR
# ============================================================

def predict_behavior(img_path):

    # Load image
    img = image.load_img(
        img_path,
        target_size=IMG_SIZE
    )

    # Convert image to array
    img_array = image.img_to_array(img)

    # Normalize
    img_array = img_array / 255.0

    # Add batch dimension
    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    # Get probabilities
    predictions = model.predict(
        img_array,
        verbose=0
    )[0]

    # Normal highest probability
    class_index = np.argmax(
        predictions
    )

    # ========================================================
    # USING_MOBILE THRESHOLD
    # ========================================================

    mobile_probability = predictions[
        MOBILE_INDEX
    ]

    if mobile_probability >= MOBILE_THRESHOLD:

        class_index = MOBILE_INDEX

    # Return behavior name
    return labels[str(class_index)]

# type: ignore

import json
import os
from functools import lru_cache
import numpy as np



BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)




MODEL_PATH = os.path.join(
    BASE_DIR, "ai_model", "behavior_model_v4.h5"
)

LABELS_PATH = os.path.join(
    BASE_DIR, "ai_model", "behavior_labels.json"
)


IMG_SIZE = (224, 224)
MOBILE_INDEX = 3
MOBILE_THRESHOLD = 0.42


@lru_cache(maxsize=1)
def get_model():
    from tensorflow.keras.models import load_model

    return load_model(MODEL_PATH, compile=False)


@lru_cache(maxsize=1)
def get_labels():
    with open(LABELS_PATH, "r") as f:
        return json.load(f)


def predict_behavior(img_path):
    from tensorflow.keras.preprocessing import image

    model = get_model()
    labels = get_labels()

    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array, verbose=0)[0]
    class_index = int(np.argmax(predictions))

    if predictions[MOBILE_INDEX] >= MOBILE_THRESHOLD:
        class_index = MOBILE_INDEX

    return labels[str(class_index)]

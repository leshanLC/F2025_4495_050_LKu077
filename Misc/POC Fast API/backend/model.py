import joblib
import numpy as np

# Load model and encoders
model = joblib.load('mushroom_model.pkl')
label_encoders = joblib.load('label_encoders.pkl')

def predict_mushroom(input_data: dict):
    try:
        # Encode input data using saved label encoders
        encoded = []
        for feature, value in input_data.items():
            le = label_encoders[feature]
            encoded.append(le.transform([value])[0])  # Transform single value
        encoded = np.array(encoded).reshape(1, -1)
        prediction = model.predict(encoded)[0]

        # Decode prediction back to 'e' or 'p'
        class_label = label_encoders['class'].inverse_transform([prediction])[0]
        return class_label
    except Exception as e:
        raise ValueError(f"Error in prediction: {str(e)}")

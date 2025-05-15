# import numpy as np
# from tensorflow import keras
# from PIL import Image, UnidentifiedImageError
# import io

# # Load the saved model (replace with your actual model path)
# model = keras.models.load_model('/Users/deogirekartik/Vscode/The_Final_Project/model/Xception_best-4.keras')

# # Class labels for tumor types
# CLASS_LABELS = ["No Tumor", "Glioma", "Meningioma", "Pituitary"]

# def predict_image(image_file):
#     """Predict the tumor type and cancer status from an uploaded image."""
#     try:
#         # Ensure the image is opened correctly and resized
#         image = Image.open(image_file).convert("RGB").resize((299, 299))
#         img_array = np.array(image) / 255.0
#         img_array = np.expand_dims(img_array, axis=0)

#         # Perform the prediction
#         predictions = model.predict(img_array)
#         predicted_class = np.argmax(predictions, axis=1)[0]
#         confidence = np.max(predictions)

#         # Determine cancer status
#         cancer_status = "Cancerous" if predicted_class > 0 else "Non-Cancerous"

#         return {
#             "class": CLASS_LABELS[predicted_class],
#             "confidence": round(float(confidence) * 100, 2),
#             "cancer_status": cancer_status
#         }

#     except UnidentifiedImageError:
#         return {"error": "Uploaded file is not a valid image."}

#     except Exception as e:
#         # Catch other exceptions and return an error message
#         return {"error": f"Prediction failed: {str(e)}"}
import numpy as np
from tensorflow import keras
from PIL import Image, UnidentifiedImageError
import io

# Load the saved model (replace with your actual model path)
model = keras.models.load_model('/Users/deogirekartik/Vscode/The_Final_Project/model/Xception_best-4.keras')

# Class labels for tumor types
CLASS_LABELS = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]

def predict_image(image_file):
    """Predict the tumor type and cancer status from an uploaded image."""
    try:
        # Ensure the image is opened correctly and resized
        image = Image.open(image_file).convert("RGB").resize((299, 299))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        # Perform the prediction
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = np.max(predictions)
        # Determine cancer status - updated logic
        # Glioma (index 1) and Pituitary (index 3) are considered cancerous
        tumor_type = CLASS_LABELS[predicted_class]
        cancer_status = "Cancerous" if tumor_type in ["Glioma", "Pituitary"] else "Non-Cancerous"
        return {
            "class": tumor_type,
            "confidence": round(float(confidence) * 100, 2),
            "cancer_status": cancer_status
        }
    except UnidentifiedImageError:
        return {"error": "Uploaded file is not a valid image."}
    except Exception as e:
        # Catch other exceptions and return an error message
        return {"error": f"Prediction failed: {str(e)}"}
# camera/views.py
import json

import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import redirect, render
from joblib import load
from keras.models import load_model
from scipy.fftpack import fft
from scipy.stats import median_abs_deviation

from .forms import RecordingForm


def upload_recording(request):
    if request.method == "POST":
        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect("camera:show_camera")
    else:
        form = RecordingForm()
    return render(request, "camera/index.html", {"form": form})


def show_camera(request):

    return render(request, "camera/index.html")


# model_path = os.path.join(os.path.dirname(__file__), )

# print(model_path)
model = load_model("camera/ml_models/initial_model2.keras")


def fall_recognition(request):
    if request.method == "POST":
        data = json.loads(request.body)

        df = process_sensor_data(data)
        # sensor_data = np.array(data["sensor_data"])
        # sensor_data = sensor_data.reshape((1, 10, 5))  # Adjust shape as needed

        scaler = load("camera/ml_models/scaler.joblib")
        X_test = df
        X_test_normalized = scaler.transform(X_test)
        time_steps = 15

        # Ensure the number of samples is divisible by time_steps
        num_test_samples = (X_test_normalized.shape[0] // time_steps) * time_steps

        X_test_final = X_test_normalized[:num_test_samples]

        # Reshape data for LSTM [samples, time steps, features]
        X_test_final = X_test_final.reshape((num_test_samples // time_steps, time_steps, X_test_final.shape[1]))

        y_pred = model.predict(X_test_final)
        prediction = np.argmax(y_pred, axis=1)
        return JsonResponse({"prediction": prediction.tolist()})
        return JsonResponse({"prediction": data})
    return JsonResponse({"error": "Invalid request method"}, status=400)


def process_sensor_data(data):
    # Define the column titles
    columns = [
        "Time(s)",
        "acc_x(g)",
        "acc_y(g)",
        "acc_z(g)",
        "gyr_x(deg/s)",
        "gyr_y(deg/s)",
        "gyr_z(deg/s)",
        # "mag_x(G)",
        # "mag_y(G)",
        # "mag_z(G)",
        "SVM_acc(g)",
        # "yaw(deg)",
        # "pitch(deg)",
        # "roll(deg)",
        "SVM_gyro(g)",
        "SVM_acc(g)_mean",
        "SVM_acc(g)_std",
        "SVM_acc(g)_median",
        "SVM_acc(g)_mad",
        "SVM_gyro(g)_mean",
        "SVM_gyro(g)_std",
        "SVM_gyro(g)_median",
        "SVM_gyro(g)_mad",
        "SVM_acc(g)_fft_mean",
        "SVM_acc(g)_fft_std",
        "SVM_gyro(g)_fft_mean",
        "SVM_gyro(g)_fft_std",
    ]

    rows = []

    # Create a DataFrame from the JSON data
    sensor_datas = data["sensor_data"]

    for sensor_data in sensor_datas:
        time = sensor_data["timestamp"] / 1000  # Convert timestamp to seconds
        acc = sensor_data["acc"]
        gyro = sensor_data["gyro"]
        # mag = sensor_data["mag"]

        # Calculate the additional metrics
        acc_x = acc["x"]
        acc_y = acc["y"]
        acc_z = acc["z"]
        gyr_x = gyro["alpha"]
        gyr_y = gyro["beta"]
        gyr_z = gyro["gamma"]
        # mag_x = mag["x"]
        # mag_y = mag["y"]
        # mag_z = mag["z"]

        SVM_acc = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
        SVM_gyro = np.sqrt(gyr_x**2 + gyr_y**2 + gyr_z**2)

        # Append row to the list
        rows.append(
            {
                "Time(s)": time,
                "acc_x(g)": acc_x,
                "acc_y(g)": acc_y,
                "acc_z(g)": acc_z,
                "gyr_x(deg/s)": gyr_x,
                "gyr_y(deg/s)": gyr_y,
                "gyr_z(deg/s)": gyr_z,
                # "mag_x(G)": mag_x,
                # "mag_y(G)": mag_y,
                # "mag_z(G)": mag_z,
                "SVM_acc(g)": SVM_acc,
                # "yaw(deg)": gyr_x,
                # "pitch(deg)": gyr_y,
                # "roll(deg)": gyr_z,
                "SVM_gyro(g)": SVM_gyro,
            }
        )

    df = pd.DataFrame(rows, columns=columns)

    # Calculate additional metrics

    window_size = 15  # Adjust the window size as needed for 1-second windows
    df["SVM_acc(g)_mean"] = df["SVM_acc(g)"].rolling(window=window_size).mean()
    df["SVM_acc(g)_std"] = df["SVM_acc(g)"].rolling(window=window_size).std()
    df["SVM_acc(g)_median"] = df["SVM_acc(g)"].rolling(window=window_size).median()
    df["SVM_acc(g)_mad"] = df["SVM_acc(g)"].rolling(window=window_size).apply(median_abs_deviation)

    df["SVM_gyro(g)_mean"] = df["SVM_gyro(g)"].rolling(window=window_size).mean()
    df["SVM_gyro(g)_std"] = df["SVM_gyro(g)"].rolling(window=window_size).std()
    df["SVM_gyro(g)_median"] = df["SVM_gyro(g)"].rolling(window=window_size).median()
    df["SVM_gyro(g)_mad"] = df["SVM_gyro(g)"].rolling(window=window_size).apply(median_abs_deviation)

    # Calculate FFT-based features for a specified window size
    def calculate_fft_features(signal):
        signal = np.array(signal)  # Convert Series to numpy array
        fft_values = fft(signal)
        fft_magnitude = np.abs(fft_values)
        return np.mean(fft_magnitude), np.std(fft_magnitude)

    # Apply FFT feature calculation on rolling windows
    df["SVM_acc(g)_fft_mean"] = (
        df["SVM_acc(g)"].rolling(window=window_size).apply(lambda x: calculate_fft_features(x)[0] if len(x) == window_size else np.nan)
    )
    df["SVM_acc(g)_fft_std"] = (
        df["SVM_acc(g)"].rolling(window=window_size).apply(lambda x: calculate_fft_features(x)[1] if len(x) == window_size else np.nan)
    )

    df["SVM_gyro(g)_fft_mean"] = (
        df["SVM_gyro(g)"].rolling(window=window_size).apply(lambda x: calculate_fft_features(x)[0] if len(x) == window_size else np.nan)
    )
    df["SVM_gyro(g)_fft_std"] = (
        df["SVM_gyro(g)"].rolling(window=window_size).apply(lambda x: calculate_fft_features(x)[1] if len(x) == window_size else np.nan)
    )

    # Select only the required columns
    # df = df[columns]
    drop_cols = ["Time(s)", "acc_x(g)", "acc_y(g)", "acc_z(g)", "gyr_x(deg/s)", "gyr_y(deg/s)", "gyr_z(deg/s)"]

    df.dropna(inplace=True)
    df.drop(columns=drop_cols, inplace=True)

    # df.to_csv(
    #     "/Users/jinho/Dev/aivlebig/SeedoPJT/seedo/media/csvs/sensor_data.csv",
    #     index=False,
    # )
    return df


# import io
# import numpy as np
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from PIL import Image
# import torch
# from torchvision.transforms import Compose, Resize, ToTensor

# # Load the MiDaS model
# model_type = "DPT_Large"  # You can also use DPT_Hybrid or MiDaS_small
# midas = torch.hub.load("intel-isl/MiDaS", model_type)
# midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

# if model_type in ["DPT_Large", "DPT_Hybrid"]:
#     transform = midas_transforms.dpt_transform
# else:
#     transform = midas_transforms.small_transform

# # Set the device to GPU if available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# midas.to(device).eval()


# @csrf_exempt
# def depth_estimation(request):
#     if request.method == "POST":
#         # Read image from the request
#         image_data = request.body
#         image = Image.open(io.BytesIO(image_data)).convert("RGB")

#         # Transform the image
#         input_batch = transform(image).to(device)

#         # Predict depth
#         with torch.no_grad():
#             prediction = midas(input_batch)

#         prediction = torch.nn.functional.interpolate(
#             prediction.unsqueeze(1),
#             size=image.size[::-1],  # (width, height)
#             mode="bicubic",
#             align_corners=False,
#         ).squeeze()

#         depth_map = prediction.cpu().numpy()

#         # Normalize depth map to 0-255 for visualization
#         depth_map = (
#             (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min()) * 255
#         )
#         depth_map = depth_map.astype(np.uint8)

#         # Convert depth map to image
#         depth_image = Image.fromarray(depth_map)

#         # Create a byte buffer to send the image
#         buf = io.BytesIO()
#         depth_image.save(buf, format="PNG")
#         buf.seek(0)

#         return HttpResponse(buf, content_type="image/png")

#     return HttpResponse(status=405)  # Method not allowed

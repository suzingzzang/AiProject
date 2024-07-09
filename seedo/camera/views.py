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
        # form = RecordingForm(request.POST, request.FILES)
        # if form.is_valid():
        #     form.save()
        return redirect("camera:show_camera")
    else:
        form = RecordingForm()
    return render(request, "camera/index.html", {"form": form})


def show_camera(request):

    return render(request, "camera/index.html")


model = load_model("camera/ml_models/initial_model2.h5")


def fall_recognition(request):
    if request.method == "POST":
        data = json.loads(request.body)
        df = process_sensor_data(data)

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
        "SVM_acc(g)",
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

        # Calculate the additional metrics
        acc_x = acc["x"]
        acc_y = acc["y"]
        acc_z = acc["z"]
        gyr_x = gyro["alpha"]
        gyr_y = gyro["beta"]
        gyr_z = gyro["gamma"]

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
                "SVM_acc(g)": SVM_acc,
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
    drop_cols = ["Time(s)", "acc_x(g)", "acc_y(g)", "acc_z(g)", "gyr_x(deg/s)", "gyr_y(deg/s)", "gyr_z(deg/s)"]

    df.dropna(inplace=True)
    df.drop(columns=drop_cols, inplace=True)

    return df

# camera/views.py
from django.shortcuts import redirect, render

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

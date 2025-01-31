import time
import mss
import numpy as np
import cv2
import os
from PIL import Image

folder = "frames"

# Create the frames folder if it doesn't exist
os.makedirs(folder, exist_ok=True)

# Initialize screen capture
with mss.mss() as sct:
    while True:
        # Capture the entire screen at full resolution
        screenshot = sct.grab(sct.monitors[1])

        # Convert to a numpy array
        frame = np.array(screenshot)

        # Convert from BGRA to BGR (drop the alpha channel)
        frame = frame[:, :, :3]

        # Convert to PIL image (useful for resizing and compression)
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Convert back to OpenCV format
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Save the frame as a compressed JPEG image
        output_path = os.path.join(folder, "frame.jpg")
        cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])  # 80% quality for compression

        print(f"📸 Screenshot saved at full res (or resized) with compression! {output_path}")

        time.sleep(2)

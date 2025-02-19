import time
import mss
import numpy as np
import cv2
import os
from PIL import Image

folder = "frames"
os.makedirs(folder, exist_ok=True)

# Set an average pixel difference threshold (tune this as needed)
DIFF_THRESHOLD = 30

previous_frame = None

with mss.mss() as sct:
    while True:
        # Capture the entire screen at full resolution
        screenshot = sct.grab(sct.monitors[1])
        frame = np.array(screenshot)
        frame = frame[:, :, :3]  # drop alpha channel

        if previous_frame is not None:
            # Calculate the absolute difference between current and previous frame
            diff = cv2.absdiff(frame, previous_frame)
            mean_diff = np.mean(diff)
            if mean_diff < DIFF_THRESHOLD:
                print("📸 Frame difference below threshold, skipping save/AI workflow")
                time.sleep(2)
                continue  # Skip further processing if change is too small

        # Update the previous frame for next iteration
        previous_frame = frame.copy()

        # (Optional) Convert to PIL and back if you need resizing or additional compression
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Save the frame as a compressed JPEG image
        output_path = os.path.join(folder, "frame.jpg")
        cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        print(f"📸 New screenshot saved: {output_path}")

        time.sleep(2)

import os
import time
import base64
import errno
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs import generate, play, set_api_key

# TODO: Look into using OpenAI Real-time API or Live Video for faster responses

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

set_api_key(os.getenv("ELEVENLABS_API_KEY"))


def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def play_audio(text):
    """Generate and play coaching audio feedback."""
    audio = generate(text, voice=os.getenv("ELEVENLABS_VOICE_ID"), model="eleven_flash_v2_5")

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narrations", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "coaching.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio)


def generate_new_line(base64_image):
    """Generate coaching prompt based on the frame."""
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze the gameplay in this image and provide coaching tips for Rocket League."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    """Use OpenAI to analyze the frame and give coaching feedback."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are a professional Rocket League coach analyzing gameplay frames.
                Provide actionable feedback, such as positioning, rotation, boost management, and mechanics.
                Be concise, clear, and encouraging. Keep responses short (1-2 sentences max).
                """,
            },
        ]
        + script
        + generate_new_line(base64_image),
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text


def main():
    script = []

    while True:
        # Path to the latest frame
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

        # Encode image in Base64
        base64_image = encode_image(image_path)

        # Analyze gameplay
        print("⚽ Coach analyzing gameplay...")
        coaching_feedback = analyze_image(base64_image, script=script)

        print("🎙️ Coach says:")
        print(coaching_feedback)

        # Play coaching feedback
        play_audio(coaching_feedback)

        # Store coaching history for context-aware analysis
        script = script + [{"role": "assistant", "content": coaching_feedback}]


if __name__ == "__main__":
    main()

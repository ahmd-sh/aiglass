import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
import time
import errno
from elevenlabs import generate, play, set_api_key

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
    audio = generate(text, voice=os.getenv("ELEVENLABS_VOICE_ID"), model="eleven_flash_v2_5")

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio)


def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the user intent in this image in a sports commentary style."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are a sports commentator narrating the sequential pictures of me using my computer as if it is a high stakes sporting moment.
                Make it snarky and funny. Don't repeat yourself. Make it SHORT 1 sentence MAXIMUM. If I do anything remotely interesting, make a big deal about it!
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
        # path to your image
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

        # getting the base64 encoding
        base64_image = encode_image(image_path)

        # analyze posture
        print("👀 Narrator is watching...")
        analysis = analyze_image(base64_image, script=script)

        print("🎙️ Narrator says:")
        print(analysis)

        play_audio(analysis)

        script = script + [{"role": "assistant", "content": analysis}]

        # wait for 5 seconds
        # time.sleep(5)


if __name__ == "__main__":
    main()

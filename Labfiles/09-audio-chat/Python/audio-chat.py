import os
import base64
import requests
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def play_audio_file(path: str):
    # Windows: opens default player
    if os.name == "nt":
        os.startfile(path)  # noqa: S606
    # macOS
    elif sys.platform == "darwin":
        os.system(f"open {path}")
    # Linux
    else:
        os.system(f"xdg-open {path}")


def main():
    try:
        load_dotenv()
        project_endpoint = os.getenv("PROJECT_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        system_message = (
            "You are an AI assistant for a produce supplier company. "
            "You receive voice messages from customers and summarize what the customer is saying, "
            "including any key information and any actions that should be taken."
        )

        project_client = AIProjectClient(
            credential=DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_managed_identity_credential=True
            ),
            endpoint=project_endpoint,
        )

        # IMPORTANT: use an API version that supports audio in chat completions
        openai_client = project_client.get_openai_client(api_version="2025-01-01-preview")

        while True:
            prompt = input("\nEnter your prompt (or type 'quit' to exit): ")
            if prompt.lower() == "quit":
                break

            file_url = "https://github.com/MicrosoftLearning/mslearn-ai-language/raw/refs/heads/main/Labfiles/09-audio-chat/data/avocados.mp3"
            r = requests.get(file_url)
            r.raise_for_status()
            audio_data = base64.b64encode(r.content).decode("utf-8")

            completion = openai_client.chat.completions.create(
                model=model_deployment,
                modalities=["text", "audio"],              # request audio output
                audio={"voice": "alloy", "format": "wav"}, # choose voice/format
                messages=[
                    {"role": "system", "content": system_message},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "input_audio",
                                "input_audio": {"data": audio_data, "format": "mp3"},
                            },
                        ],
                    },
                ],
            )

            # Text (transcript) output
            if completion.choices[0].message.audio and completion.choices[0].message.audio.transcript:
                print(completion.choices[0].message.audio.transcript)
            else:
                print(completion.choices[0].message.content)

            # Audio output -> write to file
            if completion.choices[0].message.audio and completion.choices[0].message.audio.data:
                wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
                out_path = "response.wav"
                with open(out_path, "wb") as f:
                    f.write(wav_bytes)
                print(f"Wrote audio to {out_path}")
                # play_audio_file(out_path)  # uncomment to auto-play

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    import sys
    main()

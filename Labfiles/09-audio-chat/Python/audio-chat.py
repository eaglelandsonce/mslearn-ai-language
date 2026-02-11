import os
import base64
import requests
from dotenv import load_dotenv

# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main():

    try:
        # Get configuration settings
        load_dotenv()
        project_endpoint = os.getenv("PROJECT_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        system_message = """You are an AI assistant for a produce supplier company. You receive voice messages from customers and summarize what the customer is saying, including any key information and any actions that should be taken."""

        # Initialize the project client
        project_client = AIProjectClient(
           credential=DefaultAzureCredential(
               exclude_environment_credential=True,
               exclude_managed_identity_credential=True
           ),
           endpoint=project_endpoint,
        )

        # Get a chat client
        openai_client = project_client.get_openai_client(api_version="2024-10-21")

        while True:
            prompt = input("\nEnter your prompt (or type 'quit' to exit): ")
            if prompt.lower() == "quit":
                break

            # Encode the audio file
            file_path = "https://github.com/MicrosoftLearning/mslearn-ai-language/raw/refs/heads/main/Labfiles/09-audio-chat/data/avocados.mp3"
            response = requests.get(file_path)
            response.raise_for_status()
            audio_data = base64.b64encode(response.content).decode('utf-8')

            # Get a response to audio input
            response = openai_client.chat.completions.create(
               model=model_deployment,
               messages=[
                   {"role": "system", "content": system_message},
                   { "role": "user",
                       "content": [
                       {
                           "type": "text",
                           "text": prompt
                       },
                       {
                           "type": "input_audio",
                           "input_audio": {
                               "data": audio_data,
                               "format": "mp3"
                           }
                       }
                   ] }
               ]
            )
            print(response.choices[0].message.content)

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()

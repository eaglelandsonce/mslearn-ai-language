import os
from datetime import datetime
from dotenv import load_dotenv

# Import namespaces
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound


def transcribe_command(speech_config):
    command = ''

    # Configure speech recognition
    current_dir = os.getcwd()
    audioFile = current_dir + '\\time.wav'
    playsound(audioFile)
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(command)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return command


def tell_time(speech_config):
    # Get the current time
    now = datetime.now()
    response_text = 'The time is {}:{:02d}'.format(now.hour, now.minute)

    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural'  # change this
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    # Synthesize spoken output
    responseSsml = " \
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
            <voice name='en-GB-LibbyNeural'> \
                {} \
                <break strength='weak'/> \
                Time to end this lab! \
            </voice> \
        </speak>".format(response_text)
    speak = speech_synthesizer.speak_ssml_async(responseSsml).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

    # Print the response
    print(response_text)


def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        cog_key = os.getenv('COG_SERVICE_KEY')
        cog_region = os.getenv('COG_SERVICE_REGION')

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)
        print('Ready to use speech service in:', speech_config.region)

        # Get spoken command
        command = transcribe_command(speech_config)

        # Respond to command
        if 'time' in command.lower():
            tell_time(speech_config)

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()

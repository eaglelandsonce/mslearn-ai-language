import os
from dotenv import load_dotenv

# import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient


def main():
    try:
        # Get Configuration Settings
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        # Create client using endpoint and key
        credential = AzureKeyCredential(ai_key)
        ai_client = TextAnalyticsClient(endpoint=ai_endpoint, credential=credential)

        # Analyze each text file in the reviews folder
        reviews_folder = 'reviews'
        for file_name in os.listdir(reviews_folder):
            file_path = os.path.join(reviews_folder, file_name)

            with open(file_path, encoding='utf8') as file:
                text = file.read()

            print('\n\n------------------------')
            print('Review file:', file_name)
            print('------------------------')
            print(text)

            # Get language
            detectedLanguage = ai_client.detect_language(documents=[text])[0]
            print('\n Language: {}'.format(detectedLanguage.primary_language.name))

            # Get sentiment
            sentimentAnalysis = ai_client.analyze_sentiment(documents=[text])[0]
            print("\n Sentiment: {}".format(sentimentAnalysis.sentiment))

            # Get key phrases
            phrases = ai_client.extract_key_phrases(documents=[text])[0].key_phrases
            if len(phrases) > 0:
                print("\n Key Phrases:")
                for phrase in phrases:
                    print('\t{}'.format(phrase))

            # Get entities
            entities = ai_client.recognize_entities(documents=[text])[0].entities
            if len(entities) > 0:
                print("\n Entities")
                for entity in entities:
                    print('\t{} ({})'.format(entity.text, entity.category))

            # Get linked entities
            entities = ai_client.recognize_linked_entities(documents=[text])[0].entities
            if len(entities) > 0:
                print("\n Links")
                for linked_entity in entities:
                    print('\t{} ({})'.format(linked_entity.name, linked_entity.url))

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()

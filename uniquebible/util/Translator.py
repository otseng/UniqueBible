import requests

from uniquebible import config

class Translator:

    language_mapping = {"de": "de", "el": "el", "en_GB": "en", "en_US": "en", "es": "es", "fr": "fr",
                        "hi": "hi", "it": "it", "ja": "ja", "ko": "ko", "ml": "en", "ro": "ro", "ru": "ru",
                        "zh_HANS": "zh", "zh_HANT": "zt"}

    def translate(self, text, fromLanguage="en", toLanguage="es"):
        url = config.translate_api_url + "/translate"
        api_key = config.translate_api_key
        payload = {"source": fromLanguage, "target": toLanguage, "q": text, "format": "text", "api_key": api_key}
        response = requests.post(url, json=payload)
        translation = response.json()['translatedText']
        return translation

if __name__ == "__main__":
    translator = Translator()
    print(translator.translate("hello", "es"))

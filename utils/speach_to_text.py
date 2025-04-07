import speech_recognition as sr
from pydub import AudioSegment


def speech_to_text(path: str, lang: str = "ru-RU") -> dict:
    if path.split(".")[-1] != "wav":
        AudioSegment.from_file(path).export(f"{path.rsplit('.')[0]}.wav", format="wav")
        path = f"{path.rsplit('.')[0]}.wav"

    r = sr.Recognizer()
    with sr.AudioFile(path) as src:
        audio = r.record(src)
        result = r.recognize_google(audio, language=lang, show_all=True)
        text = result["alternative"][0]["transcript"]
        return text

from playsound import playsound
from pydub import AudioSegment
import pyttsx3

def makeogg(text, name, voice):
    string = text.replace("<br>", " ")

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(voices)
    engine.setProperty('rate', 150)
    engine.setProperty('voice', voices[voice].id)
    engine.save_to_file(string, 'static/TTSaudio/'+name+'.ogg')


    engine.runAndWait()

    return name

#sound = AudioSegment.from_file("speech.mp3", format="mp3")
#sound.export("speech.ogg", format="ogg")
from playsound import playsound
from pydub import AudioSegment
import os
import pyttsx3

def makeogg(text, voice):
    string = text.replace("<br>", " ")
    path = 'static/TTSaudio/' #os.getenv('HOME') + '/python'
    num_files = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
        
    name = str(num_files+1)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(voices)
    engine.setProperty('rate', 150)
    engine.setProperty('voice', voices[voice].id)
    engine.save_to_file(string, path + name +'.ogg')


    engine.runAndWait()

    return name

#sound = AudioSegment.from_file("speech.mp3", format="mp3")
#sound.export("speech.ogg", format="ogg")
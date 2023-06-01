import whisper
import torch
global model
model = ''
def dowhisper(filename):
    audio = whisper.load_audio(filename)
    audio = whisper.pad_or_trim(audio)


    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # detect the spoken language
    #_, probs = model.detect_language(mel)
    #print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    #options = whisper.DecodingOptions(fp16 = False)
    
    # ENGLISH ONLY
    options = whisper.DecodingOptions(language = 'en')
    result = whisper.decode(model, mel, options)

    # print the recognized text
    print(result.text)
    return(result.text)



def loadModel(modename):
    torch.cuda.empty_cache()
    global model 
    model = whisper.load_model(modename)
    print("whisper: " + modename +" model loaded")
# load audio and pad/trim it to fit 30 seconds
#audio = whisper.load_audio("audio1.weba")
#dowhisper("audio.mp3")

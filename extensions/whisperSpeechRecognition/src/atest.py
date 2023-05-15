
def doTest():

    print("test is successful")
# load audio and pad/trim it to fit 30 seconds
#audio = whisper.load_audio("audio1.weba")
#dowhisper("audio.mp3")

x = '["EGFR","KRAS","TP53"]'



import json
obj1 = json.loads(x)
print (obj1[0])

import json
import logging
import os
import random
import re
import string
import wave
from base64 import b64encode
from cgi import print_arguments
from io import StringIO
from mimetypes import guess_extension

import flask

# from flask_session import Session
import requests
import torch  # pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
import whisper
from engineio.payload import Payload
from flask import (
    Blueprint,
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_socketio import SocketIO, emit, join_room, leave_room

import GlobalData as GD

# load audio and pad/trim it to fit 30 seconds
import TextToSpeech
from io_blueprint import IOBlueprint

# import GlobalData as GD


# for cuda 11.6
# if accesing whisper over network do this: https://stackoverflow.com/questions/47995355/chrome-is-not-letting-http-hosted-site-to-access-camera-microphone


print("whisper GPU = " + str(torch.cuda.is_available()))

global model
model = ""

url_prefix = "/whisper"
blueprint = IOBlueprint(
    "whisper",
    __name__,
    url_prefix=url_prefix,
    template_folder=os.path.abspath("./extensions/whisperSpeechRecognition/templates"),
    static_folder=os.path.abspath("./extensions/whisperSpeechRecognition/static"),
)


def dowhisper(filename):
    audio = whisper.load_audio(filename)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # detect the spoken language
    # _, probs = model.detect_language(mel)
    # print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    # options = whisper.DecodingOptions(fp16 = False)

    # ENGLISH ONLY
    options = whisper.DecodingOptions(language="en")
    result = whisper.decode(model, mel, options)

    # print the recognized text
    print(result.text)
    return result.text


def loadModel(modename):
    torch.cuda.empty_cache()
    global model
    model = whisper.load_model(modename)
    print("whisper: " + modename + " model loaded")


# load audio and pad/trim it to fit 30 seconds
# audio = whisper.load_audio("audio1.weba")
# dowhisper("audio.mp3")


# aTest.doTest()

loadModel("small")


@blueprint.route("/uploadAudio", methods=["POST"])
def uploadAudio():
    result = {}

    # print("upload request received")
    # path = 'static/WhisperAudio/' #os.getenv('HOME') + '/python'
    path = blueprint.static_folder + "/WhisperAudio/"
    num_files = len(
        [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    )
    thisfile = path + str(num_files + 1)

    if "audio_file" in request.files:
        file = request.files["audio_file"]
        # Get the file suffix based on the mime type.
        extname = guess_extension(file.mimetype)
        if not extname:
            abort(400)
        # Save the file to disk.
        file.save(thisfile + ".weba")
        result["text"] = dowhisper(thisfile + ".weba")
        print(result)
    return result


@blueprint.route("/uploadAudioUE4", methods=["POST"])
def uploadAudioUE4():
    result = {}
    path = blueprint.static_folder + "/WhisperAudio/"
    num_files = len(
        [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    )
    thisfile = path + str(num_files + 1)

    if request.method == "POST":
        raw = request.get_data()
        with wave.open(thisfile + ".wav", "wb") as audiofile:
            audiofile.setsampwidth(2)
            audiofile.setnchannels(2)
            audiofile.setframerate(48000)
            audiofile.writeframes(raw)
        audiofile.close()
        result["text"] = dowhisper(thisfile + ".wav")
    return result

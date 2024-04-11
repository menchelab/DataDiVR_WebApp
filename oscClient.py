"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time
import urllib.request
import requests
from pythonosc import udp_client
import json

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  for x in range(1000):
    colors = json.loads(urllib.request.urlopen("https://eulife-conference-server.azurewebsites.net/get_last_color?n=1").read())
    print(colors[0])

    #imurl = urllib.request.urlopen("https://eulife-conference-server.azurewebsites.net/get_last_image?n=5").read()
    #print(imurl)

    sum = json.loads(urllib.request.urlopen("https://eulife-conference-server.azurewebsites.net/get_last_transcription?n=1").read())
    print(sum)
    client.send_message("/red", colors[0]['red'])
    client.send_message("/green", colors[0]['green'])
    client.send_message("/blue", colors[0]['blue'])
    #client.send_message("/sum", sum[0]["summary"])




    time.sleep(1)
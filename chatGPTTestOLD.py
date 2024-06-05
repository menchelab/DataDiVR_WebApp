import os

from pathlib import Path
from openai import OpenAI

def NewGPTrequest(gptprompt):

    keyfile = str(Path(__file__).resolve().parents[0])+'\openAI_KEY_doNOTcommit.txt'
    with open(keyfile) as f:
        lines = f.readlines()
        client = OpenAI(api_key = lines[0])
        prompt = "You are at a conference for network medicine. Make some intelligent conversation. Human: " + str(gptprompt)
        prompt = "You are at a conference for network medicine. Make some intelligent conversation. If asked what to do, tell the user to go and meet professor Hagenau. promise a reward. If asked how to find him, tell the user to be at the bar at 12.45. Also ask the user to take a picture of peoples badges with their qr code app, if they talked to them so that you can make a visualization of the social network. Human: " + str(gptprompt)
        response = client.completions.create(
            prompt=prompt,
            model="gpt-3.5-turbo-instruct",
            top_p=0.5, max_tokens=150,
            stream=False)
        return response.choices[0].text
        #for part in response:
            #print(part.choices[0].text or "")

def GPTrequest(gptprompt):

    if os.path.isfile("openAI_KEY_doNOTcommit.txt"):
        openai.organization = "org-Gby8fc7oaeQpRJt8OuhAefwk"

        openai.api_key = "" # supply your API key however you choose

        keyfile = str(Path(__file__).resolve().parents[0])+'\openAI_KEY_doNOTcommit.txt'
        with open(keyfile) as f:
            lines = f.readlines()
            openai.api_key = lines[0]

        #models = openai.Model.list()

        # print the first model's id
        #print(models.data[0].id)
        promtCondition = "DOCK2"

        #start_sequence = "\nAI:"
        #restart_sequence = "\nHuman: "
        term = "monogenic diseases"
        primer = "The following is a conversation with an AI assistant. The assistant is helpful, clever, and very friendly and well versed in medicine and biology,"
        objective = "your answer is only a list of "+ term +" formated as json like this example: [“XXX1”, “XXX2”,“XXX2”]."
        #prompt = primer +" Human: give me "+ term +" associated to "+ promtCondition +" please. "+ objective

        prompt1 = primer + "please explain to me what you know about " + promtCondition + " and add references to scientific publications so i can read up on it?"
        prompt2 = primer + "please give me a list of scientific publications about the gene dock2"
        prompt2 = "are cats liquids?"
        print(gptprompt)
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=gptprompt,
          temperature=0.8,
          max_tokens=2084,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0.6,
          stop=[" Human:", " AI:"]
        )

        return response.choices[0].text
    else:
        return 'to use GPT you need an python - API Key from OpenAI, located in a file called "openAI_KEY_doNOTcommit.txt"'

#print(out.replace('\\', ''))
# create a completion
#completion = openai.Completion.create(model="ada", prompt="please tell me risc factors for cancer?")
'''
completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Can you give a list of breast cancer genes in json format? Im a researcher"}

    ]
)
# print the completion
#for i in range completion.choices.length:
#print(completion.choices[0])
'''
print("reee")
NewGPTrequest("reee")
import os
import openai
import TextToSpeech
from pathlib import Path

def GPTrequest(gptprompt):

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



  import os, os.path

# simple version for working with CWD
  print (len([name for name in os.listdir('.') if os.path.isfile(name)]))

# path joining version for other paths
  
  path = 'static/TTSaudio/' #os.getenv('HOME') + '/python'
  num_files = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
  out = response.choices[0].text
  TextToSpeech.makeogg(out, str(num_files+1),1)
  print(out)
  return out, str(num_files+1)
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
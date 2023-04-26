import os
import openai
openai.organization = "org-Gby8fc7oaeQpRJt8OuhAefwk"

openai.api_key = "" # supply your API key however you choose
with open('openAI_KEY_doNOTcommit.txt') as f:
    lines = f.readlines()
    openai.api_key = lines[0]

#models = openai.Model.list()

# print the first model's id
#print(models.data[0].id)
promtCondition = "My penis is too small"

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly and well versed in medicine, it answers by providing only a list of genes including entrez id formatted as json like this example: \n[{“entrezId”: “xxxx”, “GeneName”: “XXX1”},\n{“entrezId”: “xxx”, “GeneName”: “XXX2”},\n{“entrezId”: “xxx”, “GeneName”: “XXX2”} ]\nit provides the 20 most important genes and makes it a complete json list and is consistent with the output format and only outputs the json without any additional text or comments\n\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: \nAI: I can help provide information about genetic information. Please tell me the type of gene you would like to research.\nHuman: give me all genes associated to "+ promtCondition +" please ",
  temperature=0.8,
  max_tokens=2084,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0.6,
  stop=[" Human:", " AI:"]
)




out = response.choices[0].text
print(out)
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
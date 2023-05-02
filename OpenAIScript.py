import openai

prompt = "Tell me about the War of 1812"

response = openai.Completion.create(engine="text-davinci-003", max_tokens=50, prompt=prompt)

print(response)
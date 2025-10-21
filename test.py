#load a .env variable
import os
from dotenv import load_dotenv
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

from google import genai
client = genai.Client()

#load in single chat prompt from a txt file
with open("single_chat_prompt.txt", "r") as f:
    single_chat_prompt = f.read()

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=single_chat_prompt,
)


with open("response.txt", "w") as f:
    f.write(response.text)


#read in grading prompt from a txt file
with open("grading_prompt.txt", "r") as f:
    grading_prompt = f.read()


grade = client.models.generate_content(
    model="gemini-2.5-pro",
    contents= grading_prompt + '\n' + response.text,
)

#write the grading response to a file

with open("grading_response.txt", "w") as f:
    f.write(grade.text)

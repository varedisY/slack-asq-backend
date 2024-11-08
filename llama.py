from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from ollama import Client
from ollama import Options

client = Client(host='http://10.192.168.112:8010')

LESSONS_SYSTEM_PROMPT="You are a teacher that answers questions based only on the provided fragments from the books. Before the anwser show the fragments that you are using .Respond in Polish."
ANSWER_SYSTEM_PROMPT = "You are an assistant for the administration of 'INFOTECH' high school. Your task is to summarize and answer questions strictly and only based on the provided context. You should respond only to questions related to INFOTECH schools, relying solely on school-related documents as context. If the context, i.e., school documents, do not contain an answer to the question, you should reply that the answer is not available. Respond in Polish."




def generate_response(context, user_prompt,is_stream=False):

    response = client.chat(model='llama3.1',stream=is_stream, messages=[
        {
            "role": "assistant",
            "content": f'${ANSWER_SYSTEM_PROMPT}\n context: ${context}',

        },
    
        {
            "role": "user",
            "content": user_prompt
        }
    ], options=Options(temperature=0.0))

    # stream = client.generate(model='llama3.1',system=ANSWER_SYSTEM_PROMPT,stream=True,  prompt=f'context: ${context}\n prompt: ${user_prompt}\n')

   

    return response
  
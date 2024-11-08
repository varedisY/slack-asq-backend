import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

LESSONS_SYSTEM_PROMPT="You are a teacher that answers questions based only on the provided fragments from the books. Before the anwser show the fragments that you are using .Respond in Polish."
ANSWER_SYSTEM_PROMPT = "You are an assistant for the administration of 'INFOTECH' high school. Your task is to summarize and answer questions strictly and only based on the provided context. You should respond only to questions related to INFOTECH schools, relying solely on school-related documents as context. If the context, i.e., school documents, do not contain an answer to the question, you should reply that the answer is not available. Respond in Polish."



def generateResponse(query,context):
    chat_completion_stream = client.chat.completions.create(
    messages=[
      
        {
            "role": "system",
            "content": "You are an assistant for the administration of 'INFOTECH' high school. Your task is to summarize and answer questions strictly and only based on the provided context. Respond in Polish."
        },
        {
            "role": "system",
            "content": "Here's the provided context: " + context
        },
        {
            "role": "user",
            "content": query
        }
    ],
    model="gpt-4",
    stream=True
)


    return chat_completion_stream

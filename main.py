from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, List
from fastapi import FastAPI, UploadFile, File, Form
import os
from fastapi.middleware.cors import CORSMiddleware
import slack
import uvicorn
import file
import chunker
import qdrant
import llama
import gpt

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(slack.router)




@app.get("/ask")
def ask(query: str,collectionName:str):
    search_results = qdrant.find(query,collectionName)

    context = "\n".join(map(lambda result: result.payload["document"], search_results))

    async def response_stream() -> AsyncGenerator[str, None]:
        stream = gpt.generateResponse(query,context)
        for chunk in stream:
            yield chunk.choices[0].delta.content or ""
    return StreamingResponse(response_stream(), media_type="text/plain")



@app.post("/embed")
async def embed_files(    uploadedFiles: List[UploadFile] = File(...),  # list of uploaded files
    collectionName: str = Form(...) ):
    success_count = 0 

    for uploadedFile in uploadedFiles:
        content = await uploadedFile.read()
        file_extension = os.path.splitext(uploadedFile.filename)[1].lower()

        if file_extension == ".txt":
            text_content = content.decode("utf-8")
        elif file_extension == ".pdf":
            text_content = file.extract_text_from_pdf(content)
        else:
            return {"error": f"Unsupported file type for {uploadedFile.filename}"}

        paragraphs = chunker.semanticSplit(text_content)

        try:
            qdrant.index_paragraphs(paragraphs,collectionName)
            success_count += 1  
        except Exception as e:
            print(f"Error indexing file {uploadedFile.filename}: {e}")

    return {"success": True, "files_processed": success_count}



# @app.get("/ask")
# async def ask_question(query: str,collectionName:str): 


#     search_results = qdrant.find(query,collectionName)

#     print(search_results)
#     context = "\n".join(map(lambda result: result.payload["document"], search_results))

#     res = llama.generate_response(context, query)
#     return res['message']['content']

#     async def response_stream() -> AsyncGenerator[str, None]:
#         stream = llama.generate_response(context, query,is_stream=True)
#         for part in stream:
#             yield part["message"]['content']  
#     return StreamingResponse(response_stream(), media_type="text/plain")





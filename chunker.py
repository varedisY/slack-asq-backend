
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from semantic_router.encoders import HuggingFaceEncoder
from semantic_chunkers import StatisticalChunker

embeddings_model = HuggingFaceEmbeddings(model_name="sdadas/mmlw-e5-small")
encoder = HuggingFaceEncoder(name="sdadas/mmlw-e5-small")
chunker = StatisticalChunker(encoder=encoder)





def embed_paragraphs(paragraphs):
   
        return embeddings_model.embed_documents(paragraphs)



def semanticSplit(text):
    chunks = chunker(docs=[text])

    chunker.print(chunks[0])

    paragarphs = []
    for chunk in chunks[0]:
          text = "".join(chunk.splits)
          paragarphs.append(text)
    return paragarphs




 
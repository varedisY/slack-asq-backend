from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from qdrant_client.http.exceptions import UnexpectedResponse
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import uuid
import chunker

client = QdrantClient(url="http://10.192.168.112", port=8011)  


def index_paragraphs(paragraphs,collectionName):
    if not client.collection_exists(collectionName):
            client.create_collection(
            collection_name=collectionName,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),  
        )
    
    query_result = chunker.embed_paragraphs(paragraphs)


    client.upsert(
        collection_name=collectionName,
        points=[
            PointStruct(
                id=str(uuid.uuid4()), 
                vector=vector,  
                payload={
                    "document": paragraph, 
         
                }
            )
            for idx, (paragraph, vector) in enumerate(zip(paragraphs, query_result))  
        ]
    )



def find(queryText,collectionName):

    query_result = chunker.embed_paragraphs([queryText])

    hits = client.search(
   collection_name=collectionName,
   query_vector=query_result[0],
   limit=4)
    return hits


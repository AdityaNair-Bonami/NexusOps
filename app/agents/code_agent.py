import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

# setting up Gemini
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# setting up ChromaDB
chroma_client = chromadb.PersistentClient(path="data/vector_db")
collection = chroma_client.get_collection(name="nexus_ops_code")

def ask_nexus_ops(question: str):
    # 1. Search ChromaDB for relevant code
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    # extract the code snippets found
    context_code = "\n---\n".join(results["documents"][0])

    # 2. Build the prompt for Gemini
    prompt = f"""
    You are NexusOps, an expert AI Developer. 
    Using the following local code snippets, answer the user's question.
    If the answer isn't in the code, say you don't know based on local context.

    CONTEXT CODE:
    {context_code}

    USER QUESTION:
    {question}
    """

    # 3. Get response from Gemini
    response = client_gemini.models.generate_content(
        model="gemini-1.5-flash-latest",
        contents=prompt
    )

    return response.text
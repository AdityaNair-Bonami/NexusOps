import os
import chromadb
from chromadb.utils import embedding_functions

# setting up local storage at 'data/vector_db' which will persist our data
client = chromadb.PersistentClient(path='data/vector_db')

default_embedding = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="nexus_ops_code",
    embedding_function=default_embedding
)

def ingest_project_code(root_dir: str):
    """
    Scans the directory for python files and adds them to the vector database
    """
    ignore_dirs = {'.git', 'venv', '__pycache__', 'data'}

    documents = []
    metadatas = []
    ids = []
    count = 0

    print(f"Starting ingestion for: {root_dir}")

    for root, dirs, files in os.walk(root_dir):
        # filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                print(f"Found file: {file_path}")

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if not content.strip():
                    continue

                # for now, we store the whole file as one document
                # in next iteration, we will chunk by function
                documents.append(content)
                metadatas.append({"source": file_path, "filename": file})
                ids.append(f"id_{count}")
                count+=1
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully ingested {len(documents)} files into ChromaDB.")
        else:
            print("No valid python files found!")

if __name__ == "__main__":
    # this identifies the folder 'NexusOps' by going up two levels from this file
    # from app/core/ to app/ to NexusOps/
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    print(f"Searching for .py files in: {project_root}")
    ingest_project_code(project_root)
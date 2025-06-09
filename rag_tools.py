from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader
from config import dnd_converter_outputs_name
from pathlib import Path
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool

load_dotenv()

def ingest_documents(dnd_type: str = "magic_item"):
    print(f"Ingesting documents for DnD type: {dnd_type}...")
    # Load the CSV file
    csv_file_path = Path(f"{dnd_converter_outputs_name}_{dnd_type}.csv")
    loader = CSVLoader(file_path=csv_file_path, encoding="utf-8")
    
    # Load documents from the CSV file
    documents = loader.load()
    
    # # Print the loaded documents
    # for doc in documents:
    #     print(doc.page_content)
    #     print("Metadata:", doc.metadata)
    #     print("-" * 40)  # Separator for readability

    return documents

def create_vector_store(documents: list) -> InMemoryVectorStore:
    print("Creating vector store from documents...")
    # Create an in-memory vector store
    vector_store = InMemoryVectorStore.from_documents(documents=documents, embedding=OpenAIEmbeddings())    
    return vector_store

def create_retriever(dnd_type: str = "magic_item"):
    print(f"Creating retriever for DnD type: {dnd_type}...")
    # Ingest documents from the CSV file
    documents = ingest_documents(dnd_type=dnd_type)
    # Create a vector store from the documents
    vector_store = create_vector_store(documents)
    # Create a retriever tool from the vector store
    retriever_tool = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": 2}),
        f"{dnd_type}_retriever",
        f"Retriever for {dnd_type} examples",
    )

    return retriever_tool

if __name__ == "__main__":
    # Example usage
    dnd_type = "magic_item"  # Change this to the desired DnD type
    retriever_tool = create_retriever(dnd_type=dnd_type)
    print(retriever_tool.invoke({"query": "Find a magic item with fire damage"}))


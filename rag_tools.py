from dotenv import load_dotenv
from langchain_community.document_loaders import CSVLoader
from config import dnd_converter_outputs_name
from pathlib import Path
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from dnd_classes import DND_MAP
from typing import Literal, List, Union, get_origin, get_args
import re

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

def create_retriever(dnd_type: str = 'Magic Item', number_to_retrieve: int = 2):
    """
    Retriever for single dnd type. 
    Note that it will always retrieve number_to_retrieve documents, as long as they are available.
    Documents are separated by "\n--document-separator--\n" 
    """
    
    print(f"Creating retriever for DnD type: {dnd_type}...")
    # Process dnd type
    dnd_type_formatted = dnd_type.lower().replace(" ", "_")
    # Ingest documents from the CSV file
    documents = ingest_documents(dnd_type=dnd_type_formatted)
    # Create a vector store from the documents
    vector_store = create_vector_store(documents)
    # Create a retriever tool from the vector store
    retriever_tool = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": number_to_retrieve}),
        f"{dnd_type_formatted}_retriever",
        f"Retriever for {dnd_type} examples",
        document_separator = "\n--document-separator--\n"
    )

    return retriever_tool

def parse_dnd_items(text: str, item_class) -> List:
    """
    Parse a text containing multiple D&D magic items separated by --document-separator--
    and convert them to a list of DnDItem objects.
    
    Args:
        text (str): The raw text containing item descriptions
        item_class (type): The Pydantic model class to create instances of
        
    Returns:
        List: A list of parsed objects
    """
    
    # Get field information from the Pydantic model
    fields_info = item_class.model_fields
    
    # Split the text by document separator
    documents = text.split('--document-separator--')
    
    items = []
    
    for doc in documents:
        doc = doc.strip()
        if not doc:
            continue
            
        # Parse each field from the document
        item_data = {}
        
        # Extract each field using regex or line-by-line parsing
        lines = doc.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip keys that don't exist in the model
                if key not in fields_info:
                    continue
                
                # Get field info
                field_info = fields_info[key]
                field_type = field_info.annotation
                
                # Handle Optional types
                origin = get_origin(field_type)
                if origin is Union:  # Optional[T] is Union[T, None]
                    args = get_args(field_type)
                    if len(args) == 2 and type(None) in args:
                        # This is Optional[T], get the non-None type
                        field_type = args[0] if args[1] is type(None) else args[1]
                
                # Convert value based on field type
                if not value:  # Empty string
                    item_data[key] = None
                elif field_type == int:
                    # Try to extract number from string
                    number_match = re.search(r'(\d+)', value)
                    item_data[key] = int(number_match.group(1)) if number_match else None
                elif field_type == str:
                    item_data[key] = value
                elif get_origin(field_type) is Literal:
                    # Handle Literal types (like saving_throw_type)
                    valid_values = get_args(field_type)
                    item_data[key] = value if value in valid_values else None
                else:
                    # Default case - try to use the value as is
                    item_data[key] = value
        
        # Create item object - let Pydantic handle validation
        try:
            item = item_class(**item_data)
            items.append(item)
        except Exception as e:
            print(f"Error creating {item_class.__name__}: {e}")
            print(f"Item data: {item_data}")
    
    return items

def retrieve_similar_items(query: str = "Find a magic item with fire damage", dnd_type: str = "Magic Item") -> List:
    retriever_tool = create_retriever(dnd_type=dnd_type)
    result = retriever_tool.invoke({"query": query})
    parsed_result = parse_dnd_items(result, DND_MAP[dnd_type])
    return parsed_result

if __name__ == "__main__":
    parsed_result = retrieve_similar_items()
    print(parsed_result)
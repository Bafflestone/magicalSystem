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

def ingest_documents(dnd_type: str = "magic_item") -> list | None:
    """
    Ingests documents from a CSV file for a specified D&D type.
    
    Args:
        dnd_type (str): The type of D&D content to ingest. Defaults to "magic_item".
    
    Returns:
        list | None: A list of loaded documents if successful, None if the file doesn't exist,
                     is empty, or contains no valid documents.
    """
    print(f"Ingesting documents for DnD type: {dnd_type}...")
    # Load the CSV file
    csv_file_path = Path(f"{dnd_converter_outputs_name}_{dnd_type}.csv")
    
    # Check if file exists and is not empty
    if not csv_file_path.exists() or csv_file_path.stat().st_size == 0:
        return None
    
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
    
    Args:
        dnd_type (str): The type of D&D content to create retriever for. Defaults to 'Magic Item'.
        number_to_retrieve (int): Number of documents to retrieve. Defaults to 2.
    
    Returns:
        retriever_tool | None: A retriever tool if documents are available, None if no documents found.
    """

    print(f"Creating retriever for DnD type: {dnd_type}...")
    # Process dnd type
    dnd_type_formatted = dnd_type.lower().replace(" ", "_")
    
    # Ingest documents from the CSV file
    documents = ingest_documents(dnd_type=dnd_type_formatted)
    
    # Handle the case where no documents are available
    if documents is None:
        print(f"No documents available for DnD type: {dnd_type}. Cannot create retriever.")
        return None
    
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

def parse_dnd_objects(text: str, item_class: type) -> List:
    """
    Parse a text containing multiple D&D objects separated by --document-separator--
    and convert them to a list of the specified Pydantic model objects.
    
    Args:
        text (str): The raw text containing object descriptions
        item_class (type): The Pydantic model class to create instances of
        
    Returns:
        List: A list of parsed objects of the specified type
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
                        origin = get_origin(field_type)
                
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
                    # Handle Literal types (like saving_throw_type, magic_school)
                    valid_values = get_args(field_type)
                    item_data[key] = value if value in valid_values else None
                elif origin is list:  # Handle List types
                    # Get the inner type of the List
                    list_args = get_args(field_type)
                    if list_args:
                        inner_type = list_args[0]
                        
                        # Split the value by comma or other delimiter
                        list_values = [v.strip() for v in value.split(',') if v.strip()]
                        
                        # Handle List[Literal[...]] types
                        if get_origin(inner_type) is Literal:
                            valid_values = get_args(inner_type)
                            item_data[key] = [v for v in list_values if v in valid_values]
                        elif inner_type == str:
                            item_data[key] = list_values
                        else:
                            # Default case for other list types
                            item_data[key] = list_values
                    else:
                        # Fallback if no type args found
                        item_data[key] = [v.strip() for v in value.split(',') if v.strip()]
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
    if retriever_tool is None:
        print(f"No documents available for DnD type: {dnd_type}. Cannot retrieve similar items.")
        return None
    
    result = retriever_tool.invoke({"query": query})
    parsed_result = parse_dnd_objects(result, DND_MAP[dnd_type])
    return parsed_result

if __name__ == "__main__":
    parsed_result = retrieve_similar_items(dnd_type="Spell")
    print(parsed_result)
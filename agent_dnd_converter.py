import operator
from dotenv import load_dotenv
from typing import Annotated, TypedDict

from langchain_core.messages import (
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from llm_prompts import TYPE_PROMPT_TEMPLATE, OBJECT_TEMPLATE, SIMILAR_OBJECTS_TEMPLATE, REFLECTION_PROMPT, REFLECT_OBJECT_TEMPLATE
from dnd_classes import DnDType, DND_MAP
from config import openai_llm, ollama_llm, use_local_llm, dnd_converter_outputs_name
from pathlib import Path
import pandas as pd
from rag_tools import retrieve_similar_objects

load_dotenv()

class AgentState(TypedDict):
    description: str
    lnode: str
    dnd_type: str
    dnd_system: str
    similar_objects: dict[str] 
    draft: str
    critique: str
    revision_number: int
    max_revisions: int
    count: Annotated[int, operator.add]


class dnd_converter:
    def __init__(self):

        # Initialize the model
        if use_local_llm:
            self.model = ChatOllama(model=ollama_llm, temperature=0)
        else:
            self.model = ChatOpenAI(model=openai_llm, temperature=0)

        # Define the prompts
        self.TYPE_PROMPT_TEMPLATE = TYPE_PROMPT_TEMPLATE
        self.OBJECT_TEMPLATE = OBJECT_TEMPLATE
        self.SIMILAR_OBJECTS_TEMPLATE = SIMILAR_OBJECTS_TEMPLATE
        self.REFLECTION_PROMPT = REFLECTION_PROMPT
        self.REFLECT_OBJECT_TEMPLATE = REFLECT_OBJECT_TEMPLATE

        # Create the graph
        # Nodes
        builder = StateGraph(AgentState)
        builder.add_node("type_identifier", self.type_identifier_node)
        builder.add_node("find_similar_objects", self.find_similar_objects)
        builder.add_node("initial_generate", self.initial_generation_node)
        builder.add_node("reflect", self.reflection_node)
        builder.add_node("reflection_generate", self.reflection_generation_node)
        builder.set_entry_point("type_identifier")
        # Edges
        builder.add_conditional_edges(
            "initial_generate", self.should_continue, {END: END, "reflect": "reflect"}
        )
        builder.add_conditional_edges(
            "reflection_generate", self.should_continue, {END: END, "reflect": "reflect"}
        )
        builder.add_edge("type_identifier", "find_similar_objects")
        builder.add_edge("find_similar_objects", "initial_generate")
        builder.add_edge("reflect", "reflection_generate")

        # Compile graph with memory and interrupt states
        checkpointer = MemorySaver()
        self.graph = builder.compile(
            checkpointer=checkpointer,
            # interrupt_after=[],
        )

    # Node definitions
    def type_identifier_node(self, state: AgentState):
        messages = [
            SystemMessage(content=self.TYPE_PROMPT_TEMPLATE.format(description=state["description"], system=state["dnd_system"])),
        ]
        response = self.model.with_structured_output(DnDType).invoke(messages)
        return {
            "dnd_type": response.type,
            "lnode": "type_identifier",
            "count": 1,
        }

    def find_similar_objects(self, state: AgentState):
        query = f"Find a {state["dnd_type"]} similar to this description: {state["description"]}"
        similar_objects = retrieve_similar_objects(query = query, dnd_type=state["dnd_type"])
        return {
            "similar_objects": similar_objects,
            "lnode": "find_similar_objects",
            "count": 1,
        }
    
    def initial_generation_node(self, state: AgentState):
        dnd_class = DND_MAP[state["dnd_type"]]
        messages = [
            SystemMessage(content=self.OBJECT_TEMPLATE.format(
            dnd_type=state["dnd_type"], description=state["description"], system=state["dnd_system"]
        ))
        ]
        if state["similar_objects"] is not None:
            messages.append(SystemMessage(content=self.SIMILAR_OBJECTS_TEMPLATE.format(
            dnd_type=state["dnd_type"], similar_objects=state["similar_objects"]
        )))
        response = self.model.with_structured_output(dnd_class).invoke(messages)
        return {
            "draft": response,
            "revision_number": state.get("revision_number", 1) + 1,
            "lnode": "initial_generate",
            "count": 1,
        }

    def reflection_node(self, state: AgentState):
        messages = [
            SystemMessage(content=self.REFLECTION_PROMPT.format(
                dnd_type=state["dnd_type"],
                description=state["description"],
                system=state["dnd_system"],
                object_stat_block=state["draft"],
            )),
        ]
        response = self.model.invoke(messages)
        return {
            "critique": response.content,
            "lnode": "reflect",
            "count": 1,
        }

    def reflection_generation_node(self, state: AgentState):
        dnd_class = DND_MAP[state["dnd_type"]]
        messages = [
            SystemMessage(content=self.REFLECT_OBJECT_TEMPLATE.format(
            dnd_type=state["dnd_type"], description=state["description"], system=state["dnd_system"], object_stat_block=state["draft"], critique=state["critique"]
        )),
        ]
        response = self.model.with_structured_output(dnd_class).invoke(messages)
        return {
            "draft": response,
            "revision_number": state.get("revision_number", 1) + 1,
            "lnode": "reflection_generate",
            "count": 1,
        }

    # Conditional edge definition
    def should_continue(self, state):
        if state["revision_number"] > state["max_revisions"]:
            return END
        return "reflect"

def append_to_output_file(data):
    """Append a row of data to the output CSV file"""
    output_file = Path(f"{dnd_converter_outputs_name}_{data['dnd_type'].replace(' ', '_').lower()}.csv")
    df = pd.DataFrame([data])
    if not output_file.exists():
        df.to_csv(output_file, mode='a', index=False)
    else:
        df.to_csv(output_file, mode='a', header=False, index=False)

def save_result_to_file(result):
    """Save the result to the output file"""
    data = {
        "description": result["description"],
        "dnd_type": result["dnd_type"],
        "dnd_system": result["dnd_system"],
    }
    data.update(result["draft"].model_dump())
    # Append the result to the output file
    append_to_output_file(data)

def main():
    """Function to process a single description using the agent"""
    description = "A ritual made by arranging red dragon bones in a circle."
    max_revisions = 1
    thread = {"configurable": {"thread_id": "1"}}

    # # To get all the intermediate results
    # for s in dnd_converter().graph.stream(
    #     {
    #         "description": description,
    #         "dnd_system": "D&D 5e",
    #         "max_revisions": max_revisions,
    #         "revision_number": 0,
    #     },
    #     thread,
    # ):
    #     print(s)
    
    # To get just the final result
    result = dnd_converter().graph.invoke(
        {
            "description": description,
            "dnd_system": "D&D 5e",
            "max_revisions": max_revisions,
            "revision_number": 0,
        },
        thread,
    )

    # Save the final result to the output file
    save_result_to_file(result)

    # Return the final result
    print(result["draft"].model_dump())
    return result["draft"].model_dump()

if __name__ == "__main__":
    main()
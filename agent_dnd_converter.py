from dotenv import load_dotenv

_ = load_dotenv()

import operator
import os
from typing import Annotated, List, TypedDict

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from llm_prompts import TYPE_PROMPT_TEMPLATE, OBJECT_TEMPLATE, REFLECTION_PROMPT
from dnd_classes import DnDType, DND_MAP
from pydantic import BaseModel
from config import openai_llm

class AgentState(TypedDict):
    description: str
    lnode: str
    dnd_type: str
    dnd_system: str
    draft: str
    critique: str
    revision_number: int
    max_revisions: int
    count: Annotated[int, operator.add]


class dnd_converter:
    def __init__(self):

        # Initialize the model
        self.model = ChatOpenAI(model=openai_llm, temperature=0)

        # Define the prompts
        self.TYPE_PROMPT_TEMPLATE = TYPE_PROMPT_TEMPLATE
        self.OBJECT_TEMPLATE = OBJECT_TEMPLATE
        self.REFLECTION_PROMPT = REFLECTION_PROMPT

        # Create the graph
        # Nodes
        builder = StateGraph(AgentState)
        builder.add_node("type_identifier", self.type_identifier_node)
        builder.add_node("generate", self.generation_node)
        builder.add_node("reflect", self.reflection_node)
        builder.set_entry_point("type_identifier")
        # Edges
        builder.add_conditional_edges(
            "generate", self.should_continue, {END: END, "reflect": "reflect"}
        )
        builder.add_edge("type_identifier", "generate")
        builder.add_edge("reflect", "generate")

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

    def generation_node(self, state: AgentState):
        dnd_class = DND_MAP[state["dnd_type"]]
        messages = [
            SystemMessage(content=self.OBJECT_TEMPLATE.format(
            description=state["description"], system=state["dnd_system"]
        )),
        ]
        response = self.model.with_structured_output(dnd_class).invoke(messages)
        return {
            "draft": response,
            "revision_number": state.get("revision_number", 1) + 1,
            "lnode": "generate",
            "count": 1,
        }

    def reflection_node(self, state: AgentState):
        messages = [
            SystemMessage(content=self.REFLECTION_PROMPT.format(
                description=state["description"],
                system=state["dnd_system"],
                item_stat_block=state["draft"],
            )),
        ]
        response = self.model.invoke(messages)
        return {
            "critique": response.content,
            "lnode": "reflect",
            "count": 1,
        }

    # Conditional edge definition
    def should_continue(self, state):
        if state["revision_number"] > state["max_revisions"]:
            return END
        return "reflect"

def main():
    """Function to process a single description using the agent"""
    description = "A metal scimitar that is engulfed by flame."
    max_revisions = 1
    thread = {"configurable": {"thread_id": "1"}}

    # To get all the intermediate results
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
    print(result["draft"].model_dump())

    return result["draft"].model_dump()

if __name__ == "__main__":
    main()
"""Minimal LangGraph start->end demo

Run this script to see a tiny StateGraph in action.
Usage:
    python Backend/services/langgraph_dummy.py

This script is safe to run even if `langgraph` is not installed; it will print an instruction.
"""
import os
import sys

try:
    from langgraph.graph import StateGraph, END
except Exception:
    print("langgraph is not installed in your environment. To install: pip install langgraph")
    sys.exit(0)

from typing import TypedDict, List, Dict, Optional

# Define a minimal state type
class DummyState(TypedDict):
    counter: int

# Simple nodes
def start_node(state: DummyState):
    print("Node: start_node running")
    state.setdefault('counter', 0)
    state['counter'] += 1
    return {'counter': state['counter']}

def mid_node(state: DummyState):
    print("Node: mid_node running")
    state['counter'] += 2
    return {'counter': state['counter']}

def end_node(state: DummyState):
    print("Node: end_node running")
    state['counter'] += 3
    print(f"Final counter value: {state['counter']}")
    return {}

if __name__ == '__main__':
    print("Building a minimal StateGraph...")
    graph = StateGraph(DummyState)

    graph.add_node('start', start_node)
    graph.add_node('middle', mid_node)
    graph.add_node('end_node', end_node)

    graph.set_entry_point('start')

    # edges: start -> middle -> end
    graph.add_edge('start', 'middle')
    graph.add_edge('middle', 'end_node')
    graph.add_edge('end_node', END)

    app = graph.compile()

    print("Running graph (stream)...\n")
    initial = {'counter': 0}
    for output in app.stream(initial):
        print("Output chunk:", output)

    print("\nGraph run complete.")
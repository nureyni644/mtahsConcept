import json
import os
from typing import Literal
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from app.tools.manim import generate_manim_script, execute_manim_with_audio
import re
load_dotenv()

client = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    api_key=os.getenv("NVIDIA_API_KEY"), 
    temperature=0.2,
    top_p=0.7,
    max_completion_tokens=8192,  # Augmenté pour éviter la troncature
)

tools = [generate_manim_script, execute_manim_with_audio]
llm_with_tools = client.bind_tools(tools)

SYSTEM_PROMPT = """Tu es un assistant spécialisé dans la création de vidéos éducatives Manim.

WORKFLOW OBLIGATOIRE pour créer une vidéo :
1. TOUJOURS appeler d'abord l'outil `generate_manim_script` avec le concept demandé
2. ENSUITE appeler l'outil `execute_manim_with_audio` avec les 3 valeurs retournées:
   - code: le code Python retourné
   - narration: le texte de narration retourné  
   - math_scene: le class_name retourné

IMPORTANT:
- Tu DOIS appeler les deux outils dans cet ordre
- Ne génère JAMAIS de code toi-même, utilise TOUJOURS generate_manim_script
- Après execute_manim_with_audio, indique à l'utilisateur le résultat
"""

def parse_tool_call_from_content(content: str) -> dict | None:
    """Parse un tool call depuis le content si le modèle l'a mis là par erreur."""
    try:
        # Chercher un JSON dans le content
        json_match = re.search(r'\{.*"name".*"parameters".*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if "name" in data and "parameters" in data:
                return data
    except:
        pass
    return None

def agent(state: MessagesState):
    messages = state['messages']
    
    # Ajouter le system prompt s'il n'existe pas
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm_with_tools.invoke(messages)
    
    # Vérifier si le modèle a mis un tool call dans le content au lieu de tool_calls
    if not response.tool_calls and response.content:
        parsed = parse_tool_call_from_content(response.content)
        if parsed:
            # Convertir en vrai tool call
            response.tool_calls = [{
                "name": parsed["name"],
                "args": parsed["parameters"],
                "id": f"call_{hash(str(parsed))}"
            }]
            response.content = ""
    
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    tools_condition,
)
builder.add_edge("tools", "agent")

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {"messages": [HumanMessage(content="Explique le concept de limite")]},
        {"recursion_limit": 15}
    )
    
    # Afficher le résultat final
    for msg in result["messages"]:
        print(f"\n{'='*50}")
        print(f"Type: {type(msg).__name__}")
        if hasattr(msg, 'content') and msg.content:
            content = str(msg.content)
            print(f"Content: {content[:500]}{'...' if len(content) > 500 else ''}")
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"Tool calls: {[tc['name'] for tc in msg.tool_calls]}")
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool
def search_solution(query: str):
    """Effectue une recherche sur Internet pour trouver des solutions à des erreurs ou problèmes techniques.
    Utilise cet outil quand l'exécution de Manim échoue pour trouver comment corriger le code.
    Pas besoin de clé API.
    """
    search = DuckDuckGoSearchRun()
    return search.run(query)

import os
import re
import glob
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
from subprocess import run
load_dotenv()

llm = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct",
    api_key=os.getenv("NVIDIA_API_KEY"), 
    temperature=0.2,
    top_p=0.7,
    max_completion_tokens=8192,
)

@tool
def generate_manim_script(concept: str) -> Dict[str, str]:
    """
    ÉTAPE 1/2 - Génère un script Python Manim(manim-voiceover) avec narration synchronisée.
    """
    print("in generate_manim_script")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            Vous êtes un expert en visualisation mathématique avec Manim et manim-voiceover.

            OBJECTIF :
            Générer du code Manim pédagogique pour expliquer un concept mathématique,
            avec animation claire, synchronisation voix-off et gestion correcte des objets.

            PRINCIPES FONDAMENTAUX :
            - Être STRICTEMENT pédagogique
            - Montrer uniquement ce qui est nécessaire à la compréhension
            - Ne jamais surcharger visuellement la scène
            - Chaque élément affiché doit avoir un objectif pédagogique clair

            ────────────────────────────────────────
            GESTION OBLIGATOIRE DES OBJETS MANIM
            ────────────────────────────────────────
            - Manim ne supprime PAS automatiquement les objets
            - Aucun Mobject ne doit rester à l’écran sans justification pédagogique
            - Après chaque étape explicative, les objets précédents DOIVENT être supprimés
            - Utiliser explicitement AU MOINS UNE des méthodes suivantes :
            - self.play(FadeOut(...))
            - self.play(Uncreate(...))
            - self.clear() (uniquement entre grandes étapes)
            - Regrouper les objets liés avec VGroup pour faciliter leur suppression
            - Chaque nouvelle idée visuelle commence avec une scène propre

            ────────────────────────────────────────
            STRUCTURE PÉDAGOGIQUE OBLIGATOIRE
            ────────────────────────────────────────
            - Le code doit être découpé en étapes pédagogiques clairement commentées :
            # Étape 1 : ...
            # Étape 2 : ...
            - Chaque étape DOIT respecter le cycle suivant :
            1. Création des objets visuels
            2. Animation synchronisée avec la voix-off
            3. Nettoyage explicite de la scène (FadeOut / Uncreate / clear)

            ────────────────────────────────────────
            GESTION DE LA VOIX-OFF
            ────────────────────────────────────────
            - Utiliser manim-voiceover avec GTTSService(lang="fr")
            - Chaque voix-off doit être encapsulée dans :
            with self.voiceover(text=...) as tracker:
            - Toujours attendre la fin de la voix-off :
            self.wait(tracker.duration)
            - Éviter STRICTEMENT le chevauchement des trackers de voix-off

            ────────────────────────────────────────
            STRUCTURE DE CODE OBLIGATOIRE
            ────────────────────────────────────────
            Le code généré DOIT respecter exactement cette structure :

            ```python
            from manim import *
            from manim_voiceover import VoiceoverScene
            from manim_voiceover.services.gtts import GTTSService

            class NomDeLaScene(VoiceoverScene):
                def construct(self):
                    self.set_speech_service(GTTSService(lang="fr"))

                    # Étape 1 : ...
                    ...
            ```
        
            RÈGLES OBLIGATOIRES :
            - Le code doit etre propre et fonctionnel
            - Eviter d'utiliser des commandes latex qui n'existent pas
            - Soit creatif avec les animations et les effets visuels
            - Soit pedagogique avec les animations et les effets visuels
            - Soit interactif avec les animations et les effets visuels
        
            

            FORMAT DE SORTIE :
            ===CODE===
            [code Python]
            ===CLASS_NAME===
            [Nom de classe]
            """),
                ("user", "Explique ce concept avec Manim : {concept}")
            ])



    
    chain = prompt | llm
    response = chain.invoke({"concept": concept})
    content = response.content
    
    code_pattern = r"===CODE===\s*(.*?)\s*===CLASS_NAME==="
    class_name_pattern = r"===CLASS_NAME===\s*(\w+)"
    
    code_match = re.search(code_pattern, content, re.DOTALL)
    class_name_match = re.search(class_name_pattern, content, re.DOTALL)
    
    if not (code_match and class_name_match):
        code_match = code_match or re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL)
        if not class_name_match and code_match:
            class_name_match = re.search(r"class\s+(\w+)\s*\(", code_match.group(1))

    if code_match and class_name_match:
        code = code_match.group(1).strip()
        code = re.sub(r'^```python\s*', '', code)
        code = re.sub(r'\s*```$', '', code)
        
        return {
            "code": code,
            "class_name": class_name_match.group(1).strip()
        }
    
    fallback_class = re.search(r"class\s+(\w+)\s*\(", content)
    fallback_code = re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL)
    
    if fallback_code and fallback_class:
        # print("fallback_code", fallback_code.group(1))
        print("fallback_class", fallback_class.group(1))    
        return {
            "code": fallback_code.group(1).strip(),
            "narration": "",
            "class_name": fallback_class.group(1).strip()
        }

    return {
        "code": "# Erreur\n" + content,
        "narration": "",
        "class_name": "ErrorScene"
    }


@tool
def execute_manim_with_audio(code: str, math_scene: str) -> Dict[str, Any]:
    """
    ÉTAPE 2/2 - Exécute le code Python.
    """
    print("in execute_manim_with_audio")
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_SCENE_DIR = os.path.join(CURRENT_DIR, "scene")
    
    for dir_path in [OUTPUT_SCENE_DIR]:
        os.makedirs(dir_path, exist_ok=True)
    
    file_code = os.path.join(OUTPUT_SCENE_DIR, "scene.py")
    import datetime
    
    final_video = os.path.join(OUTPUT_SCENE_DIR, f"{math_scene}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    
    try:
        with open(file_code, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Code écrit: {file_code}")
        
        manim_cmd = ["manim", "-qm", "-o", final_video, file_code, math_scene]        
        result = run(manim_cmd, capture_output=True, text=True, cwd=OUTPUT_SCENE_DIR)
        
        if result.returncode != 0:
            return {
                "success": False,
                "video_path": None,
                "message": f"Erreur Manim: {result.stderr[:500]}",
                "metadata": {}
            }
        # zupprimer le dossier media et
        # os.removedirs(os.path.join(OUTPUT_SCENE_DIR, "media"))
        shutil.rmtree(os.path.join(OUTPUT_SCENE_DIR, "media"))
        srt_file = final_video.replace(".mp4", ".srt")
        wav_file = final_video.replace(".mp4", ".wav")
        os.remove(os.path.join(OUTPUT_SCENE_DIR, srt_file))
        os.remove(os.path.join(OUTPUT_SCENE_DIR, wav_file))
        return {
            "success": True,
            "video_path": final_video,
            "message": "Vidéo générée avec succès",
            "metadata": {}
        }
        
    except Exception as e:
        return {
            "success": False,
            "video_path": None,
            "message": f"Erreur Manim: {str(e)[:500]}",
            "metadata": {}
         }
            




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
    model="meta/llama-3.3-70b-instruct",
    api_key=os.getenv("NVIDIA_API_KEY"), 
    temperature=0.2,
    top_p=0.7,
    max_completion_tokens=8192,
)

@tool
def generate_manim_script(concept: str) -> Dict[str, str]:
    """
    ÉTAPE 1/2 - Génère un script Python Manim avec narration synchronisée.
    """
    print("in generate_manim_script")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Vous êtes un expert en visualisation mathématique avec Manim.

    OBJECTIF : Générer du code Manim SIMPLE et DIRECT avec des marqueurs audio.

    PRINCIPE IMPORTANT : 
    - Restez SIMPLE et concentré sur le concept demandé
    - N'ajoutez PAS d'éléments géométriques complexes ou de démonstrations élaborées
    - Montrez seulement ce qui est nécessaire pour expliquer le concept

    STRUCTURE OBLIGATOIRE :
    ```python
    from manim import *

    class ConceptVisualization(Scene):
        def construct(self):
            # === SEGMENT 1 ===
            # AUDIO: "Texte de narration"
            title = Text("Mon Concept", font_size=48)
            self.play(Write(title))
            self.wait(3)
            
            # === SEGMENT 2 ===
            # AUDIO: "Texte suivant"
            circle = Circle(radius=2, color=BLUE)
            self.play(Create(circle))
            self.wait(4)
    ```

    RÈGLES :
    1. Héritez de Scene (PAS VoiceoverScene)
    2. N'importez PAS manim_voiceover
    3. Chaque segment : `# === SEGMENT N ===` puis `# AUDIO: "texte"`
    4. self.wait(X) : 1.5 secondes pour 10-12 mots (soyez généreux avec les pauses)
    5. Phrases claires (15-30 mots max)
    6. 10-15 segments pour une explication complète et détaillée
    7. **DURÉE MINIMALE : 30 secondes** (calculez les self.wait() pour atteindre cette durée)
    8. Ajoutez des EXEMPLES CONCRETS et des CAS PRATIQUES
    9. Progression graduelle : introduction → définition → exemple → formule → application
    10. Utilisez self.play(FadeOut(...)) pour enlever les éléments anciens si nécessaire
    11. Ajoutez des animations intermédiaires pour illustrer les étapes

    POSITIONNEMENT :
    - to_edge(UP/DOWN/LEFT/RIGHT)
    - next_to(objet, direction, buff=0.3)
    - move_to(ORIGIN)
    - shift(UP/DOWN/LEFT/RIGHT)


    FORMAT DE SORTIE :
    ===CODE===
    [code Python]
    ===NARRATION===
    [Textes AUDIO]
    ===CLASS_NAME===
    [Nom de classe]
    """),
        ("user", "Explique ce concept avec Manim : {concept}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"concept": concept})
    content = response.content
    
    code_pattern = r"===CODE===\s*(.*?)\s*===NARRATION==="
    narration_pattern = r"===NARRATION===\s*(.*?)\s*===CLASS_NAME==="
    class_name_pattern = r"===CLASS_NAME===\s*(\w+)"
    
    code_match = re.search(code_pattern, content, re.DOTALL)
    narration_match = re.search(narration_pattern, content, re.DOTALL)
    class_name_match = re.search(class_name_pattern, content, re.DOTALL)
    
    if not (code_match and narration_match and class_name_match):
        code_match = code_match or re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL)
        if not class_name_match and code_match:
            class_name_match = re.search(r"class\s+(\w+)\s*\(", code_match.group(1))

    if code_match and class_name_match:
        code = code_match.group(1).strip()
        code = re.sub(r'^```python\s*', '', code)
        code = re.sub(r'\s*```$', '', code)
        
        narration = narration_match.group(1).strip() if narration_match else ""
        
        return {
            "code": code,
            "narration": narration,
            "class_name": class_name_match.group(1).strip()
        }
    
    fallback_class = re.search(r"class\s+(\w+)\s*\(", content)
    fallback_code = re.search(r"```python\s*(.*?)\s*```", content, re.DOTALL)
    
    if fallback_code and fallback_class:
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


def extract_audio_segments(code: str) -> list:
    """Extrait les segments audio du code."""
    pattern = r'# AUDIO: "([^"]+)"'
    return re.findall(pattern, code)


async def generate_audio_segments(segments: list, output_dir: str) -> list:
    """Génère les fichiers audio."""
    import edge_tts
    
    audio_files = []
    for i, text in enumerate(segments):
        output_file = os.path.join(output_dir, f"segment_{i}.mp3")
        communicate = edge_tts.Communicate(text, "fr-FR-HenriNeural")
        await communicate.save(output_file)
        audio_files.append(output_file)
        print(f"Audio {i}: {text[:30]}...")
    
    return audio_files


def get_duration(file_path: str) -> float:
    """Retourne la durée d'un fichier."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    result = run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def concatenate_audio_files(audio_files: list, output_path: str) -> None:
    """Concatène les fichiers audio."""
    if len(audio_files) == 0:
        return
    if len(audio_files) == 1:
        shutil.copy(audio_files[0], output_path)
        return
    
    list_file = output_path + ".txt"
    with open(list_file, "w") as f:
        for audio in audio_files:
            f.write(f"file '{audio}'\n")
    
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
    run(cmd, capture_output=True, text=True)
    os.remove(list_file)


@tool
def execute_manim_with_audio(code: str, narration: str, math_scene: str) -> Dict[str, Any]:
    """
    ÉTAPE 2/2 - Exécute le code Manim et ajoute l'audio.
    """
    print("in execute_manim_with_audio")
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_SCENE_DIR = os.path.join(CURRENT_DIR, "scene")
    AUDIO_DIR = os.path.join(OUTPUT_SCENE_DIR, "audio")
    
    for dir_path in [OUTPUT_SCENE_DIR, AUDIO_DIR]:
        os.makedirs(dir_path, exist_ok=True)
    
    file_code = os.path.join(OUTPUT_SCENE_DIR, "scene.py")
    audio_combined = os.path.join(AUDIO_DIR, "combined.mp3")
    final_video = os.path.join(OUTPUT_SCENE_DIR, "final_output.mp4")
    
    try:
        # 1. Extraire et générer audio
        segments = extract_audio_segments(code)
        print(f"Segments audio: {len(segments)}")
        
        if not segments and narration:
            segments = [s.strip() for s in narration.split('\n') if s.strip()]
        
        audio_duration = 0
        if segments:
            print("Génération audio...")
            audio_files = asyncio.run(generate_audio_segments(segments, AUDIO_DIR))
            concatenate_audio_files(audio_files, audio_combined)
            audio_duration = get_duration(audio_combined)
            print(f"Audio: {audio_duration:.1f}s")
        
        # 2. Écrire et exécuter Manim
        with open(file_code, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Code écrit: {file_code}")
        
        manim_cmd = ["manim", "-qm", "-o", "scene_video.mp4", file_code, math_scene]
        print("Exécution Manim...")
        
        result = run(manim_cmd, capture_output=True, text=True, cwd=OUTPUT_SCENE_DIR)
        
        if result.returncode != 0:
            return {
                "success": False,
                "video_path": None,
                "message": f"Erreur Manim: {result.stderr[:500]}",
                "metadata": {}
            }
        
        # 3. Trouver la vidéo
        videos = glob.glob(os.path.join(OUTPUT_SCENE_DIR, "media", "videos", "**", "*.mp4"), recursive=True)
        
        if not videos:
            return {
                "success": False,
                "video_path": None,
                "message": "Vidéo non trouvée",
                "metadata": {}
            }
        
        manim_video = videos[0]
        video_duration = get_duration(manim_video)
        print(f"Vidéo: {video_duration:.1f}s")
        
        # 4. Combiner vidéo + audio
        if segments and os.path.exists(audio_combined):
            print("Combinaison vidéo + audio...")
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", manim_video,
                "-i", audio_combined,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                final_video
            ]
            result = run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Erreur FFmpeg: {result.stderr[:200]}")
                print("Copie de la vidéo sans audio...")
                shutil.copy(manim_video, final_video)
            else:
                print("Audio ajouté avec succès!")
        else:
            print("Aucun audio à ajouter, copie de la vidéo Manim...")
            shutil.copy(manim_video, final_video)
    
        media_dir = os.path.join(OUTPUT_SCENE_DIR, "media")
        if os.path.exists(media_dir):
            try:
                shutil.rmtree(media_dir)
                print(f"Dossier {media_dir} supprimé")
            except Exception as e:
                print(f"Erreur lors de la suppression de {media_dir}: {e}")
        
        # Supprimer le dossier audio dans scene
        if os.path.exists(AUDIO_DIR):
            try:
                shutil.rmtree(AUDIO_DIR)
                print(f"✅ Dossier {AUDIO_DIR} supprimé")
            except Exception as e:
                print(f"⚠️ Erreur lors de la suppression de {AUDIO_DIR}: {e}")
        
        return {
            "success": True,
            "video_path": final_video,
            "message": f"Vidéo générée: {final_video}",
            "metadata": {
                "scene_class": math_scene,
                "audio_segments": len(segments),
                "video_duration": video_duration,
                "audio_duration": audio_duration
            }
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "video_path": None,
            "message": f"Erreur: {str(e)}",
            "metadata": {"traceback": traceback.format_exc()}
        }




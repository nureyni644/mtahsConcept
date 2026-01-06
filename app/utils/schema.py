from pydantic import BaseModel, Field
from typing import Literal

class Classifier(BaseModel):
    label: Literal["positif", "negatif", "neutre"] = Field(
        ..., 
        description="Sentiment du texte : positif, negatif ou neutre"
    )
    score: float = Field(
        ..., 
        description="Score de confiance entre 0 et 1"
    )

class ResponseByManim(BaseModel):
    code: str = Field(..., description="Code Python Manim")
    narration: str = Field(..., description="Narration pour la vidéo")
    class_name: str = Field(..., description=f"Nom de la classe principale dans le code")
    
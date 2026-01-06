from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class TestVoiceover(VoiceoverScene):
    def construct(self):
        # Utiliser Google Text-to-Speech (gratuit, pas besoin d'API key)
        self.set_speech_service(GTTSService(lang="fr"))
        
        # Segment 1
        with self.voiceover(text="Bienvenue dans cette démonstration de synchronisation audio.") as tracker:
            title = Text("Manim Voiceover", font_size=48)
            self.play(Write(title))
        
        # Segment 2
        with self.voiceover(text="Observez comment le cercle apparaît en parfaite synchronisation.") as tracker:
            circle = Circle(radius=2, color=BLUE)
            self.play(Create(circle))
        
        # Segment 3
        with self.voiceover(text="Et maintenant, une transformation vers un carré.") as tracker:
            square = Square(side_length=3, color=RED)
            self.play(Transform(circle, square))
        
        self.wait(1)
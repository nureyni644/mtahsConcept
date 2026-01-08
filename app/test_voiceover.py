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




class TheoremePythagore(VoiceoverScene):
    def construct(self):
        # Initialiser le service de synthèse vocale
        self.set_speech_service(GTTSService(lang="fr"))
        
        # Créer un triangle rectangle
        triangle = Polygon(
            ORIGIN, RIGHT * 3, RIGHT * 3 + UP * 4,
            color=BLUE
        )
        
        with self.voiceover(text="Voici un triangle rectangle") as tracker:
            self.play(Create(triangle))
            self.wait(tracker.duration)
        
        # Ajouter les labels des côtés
        a_label = MathTex("a").next_to(triangle, DOWN)
        b_label = MathTex("b").next_to(triangle, RIGHT)
        c_label = MathTex("c").move_to(triangle.get_center() + LEFT * 2)
        
        with self.voiceover(text="Nommons les côtés a, b et c") as tracker:
            self.play(Write(a_label), Write(b_label), Write(c_label))
        
        # Afficher la formule
        formule = MathTex("a^2 + b^2 = c^2")
        formule.to_edge(UP)
        
        with self.voiceover(text="Le théorème de Pythagore nous dit que a carré plus b carré égale c carré") as tracker:
            self.play(Write(formule))
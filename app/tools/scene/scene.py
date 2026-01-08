from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class DeriveeFonction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="fr"))

        # Étape 1 : Introduction
        with self.voiceover(text="La dérivée d'une fonction est une mesure de la variation de la fonction à un point donné.") as tracker:
            fonction = MathTex("f(x) = x^2").scale(1.5)
            self.play(Write(fonction))
            self.wait(tracker.duration)
            self.play(FadeOut(fonction))

        # Étape 2 : Définition de la dérivée
        with self.voiceover(text="La dérivée d'une fonction f à un point x est notée f'(x) et est définie comme la limite de la différence quotient lorsque l'incrément de x tend vers zéro.") as tracker:
            definition = MathTex("f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}").scale(1.5)
            self.play(Write(definition))
            self.wait(tracker.duration)
            self.play(FadeOut(definition))

        # Étape 3 : Exemple de calcul de dérivée
        with self.voiceover(text="Par exemple, pour la fonction f(x) = x^2, on peut calculer la dérivée en utilisant la définition.") as tracker:
            exemple = MathTex("f'(x) = \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h}").scale(1.5)
            self.play(Write(exemple))
            self.wait(tracker.duration)
            self.play(FadeOut(exemple))

            calcul = MathTex("f'(x) = \lim_{h \to 0} \frac{x^2 + 2hx + h^2 - x^2}{h}").scale(1.5)
            self.play(Write(calcul))
            self.wait(tracker.duration)
            self.play(FadeOut(calcul))

            resultat = MathTex("f'(x) = 2x").scale(1.5)
            self.play(Write(resultat))
            self.wait(tracker.duration)
            self.play(FadeOut(resultat))

        # Étape 4 : Interprétation géométrique
        with self.voiceover(text="La dérivée peut également être interprétée géométriquement comme la pente de la tangente à la courbe de la fonction au point x.") as tracker:
            graphique = FunctionGraph(lambda x: x**2, x_range=[-2, 2], color=BLUE).scale(1.5)
            self.play(Write(graphique))
            self.wait(tracker.duration)
            self.play(FadeOut(graphique))

            tangente = Line(start=[-1, 1], end=[1, 3], color=RED).scale(1.5)
            self.play(Write(tangente))
            self.wait(tracker.duration)
            self.play(FadeOut(tangente))

        # Étape 5 : Conclusion
        with self.voiceover(text="En résumé, la dérivée d'une fonction est une mesure de la variation de la fonction à un point donné et peut être calculée en utilisant la définition ou interprétée géométriquement comme la pente de la tangente à la courbe de la fonction.") as tracker:
            conclusion = Text("La dérivée est un outil puissant pour analyser les fonctions.").scale(1.5)
            self.play(Write(conclusion))
            self.wait(tracker.duration)
            self.play(FadeOut(conclusion))

        self.clear()
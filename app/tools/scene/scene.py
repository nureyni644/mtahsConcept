from manim import *

class LimiteVisualization(Scene):
    def construct(self):
        # === SEGMENT 1 ===
        # AUDIO: "Bienvenue dans cette explication sur les limites en mathématiques."
        title = Text("Limite", font_size=48)
        self.play(Write(title))
        self.wait(6)
        
        # === SEGMENT 2 ===
        # AUDIO: "La limite représente la valeur que tend à atteindre une fonction lorsqu'une variable s'approche d'un certain point."
        definition = Text("La limite est la valeur que tend à atteindre une fonction", font_size=24)
        self.play(Create(definition), FadeOut(title))
        self.wait(8)
        
        # === SEGMENT 3 ===
        # AUDIO: "Par exemple, considérons la fonction f(x) = 2x."
        exemple = Text("f(x) = 2x", font_size=36)
        self.play(Write(exemple), FadeOut(definition))
        self.wait(5)
        
        # === SEGMENT 4 ===
        # AUDIO: "Si on s'approche de x = 2, la fonction f(x) tend vers 4."
        valeur = Text("f(2) = 4", font_size=36)
        self.play(Write(valeur), FadeOut(exemple))
        self.wait(6)
        
        # === SEGMENT 5 ===
        # AUDIO: "La notation mathématique pour la limite est lim x→a f(x) = L."
        notation = Text("lim x→a f(x) = L", font_size=36)
        self.play(Write(notation), FadeOut(valeur))
        self.wait(7)
        
        # === SEGMENT 6 ===
        # AUDIO: "Ici, L est la valeur de la limite, a est le point d'approche et f(x) est la fonction."
        explication = Text("L : valeur de la limite, a : point d'approche, f(x) : fonction", font_size=24)
        self.play(Write(explication), FadeOut(notation))
        self.wait(9)
        
        # === SEGMENT 7 ===
        # AUDIO: "La limite peut être utilisée pour étudier le comportement d'une fonction près d'un point."
        utilisation = Text("Étudier le comportement d'une fonction près d'un point", font_size=24)
        self.play(Write(utilisation), FadeOut(explication))
        self.wait(7)
        
        # === SEGMENT 8 ===
        # AUDIO: "Par exemple, pour trouver la limite de f(x) = 1/x lorsqu'on s'approche de x = 0."
        exemple2 = Text("lim x→0 1/x", font_size=36)
        self.play(Write(exemple2), FadeOut(utilisation))
        self.wait(6)
        
        # === SEGMENT 9 ===
        # AUDIO: "La limite dans ce cas est infinie, car la fonction tend vers l'infini positif ou négatif."
        resultat = Text("La limite est infinie", font_size=36)
        self.play(Write(resultat), FadeOut(exemple2))
        self.wait(7)
        
        # === SEGMENT 10 ===
        # AUDIO: "En résumé, la limite est un outil puissant pour comprendre le comportement des fonctions en mathématiques."
        conclusion = Text("La limite : un outil pour comprendre les fonctions", font_size=24)
        self.play(Write(conclusion), FadeOut(resultat))
        self.wait(8)
        
        # === SEGMENT 11 ===
        # AUDIO: "Grâce à la limite, nous pouvons analyser et prédire le comportement de fonctions complexes."
        application = Text("Analyser et prédire le comportement de fonctions complexes", font_size=24)
        self.play(Write(application), FadeOut(conclusion))
        self.wait(9)
        
        # === SEGMENT 12 ===
        # AUDIO: "Enfin, la limite est un concept fondamental qui ouvre la voie à de nombreuses applications en mathématiques et en sciences."
        final = Text("La limite : un concept fondamental en mathématiques et en sciences", font_size=24)
        self.play(Write(final), FadeOut(application))
        self.wait(10)
from manim import *

class MathScene(Scene):
    def construct(self):
        cercle = Circle(radius=2, color=BLUE)
        self.play(Create(cercle))
        self.wait()

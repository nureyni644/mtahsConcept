
from app.tools.manim import execute_manim_with_audio

code = """
from manim import *

class TestScene(Scene):
    def construct(self):
        c = Circle()
        self.play(Create(c))
"""

narration = "This is a test narration."
math_scene = "TestScene"

print("Running execute_manim_with_audio...")
result = execute_manim_with_audio(code, narration, math_scene)
print("Result:", result)

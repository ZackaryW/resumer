from resumer.core.generator import Generator

def generate(copyTempFolder : bool = False):
    gen = Generator(
        ensuringFiles=[
            "awesome_ready.tex", "awesome-cv.cls"
        ]
    )
    gen._data
    setattr(
        gen, "generateSteps", gen.generateSteps + [
            "xelatex -interaction=nonstopmode pandoc.out",
            "!os.rename('pandoc.pdf', 'output.pdf')"
        ]
    )
    gen.generate(output=["output.pdf"], copyTempFolder=copyTempFolder)

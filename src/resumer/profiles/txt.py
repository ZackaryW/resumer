from resumer.core.generator import Generator


def generate(copyTempFolder : bool = False):
    gen = Generator(
        ensuringFiles=[
            "txt_ready.txt"
        ]
    )
    gen._data
    setattr(
        gen, "generateSteps", gen.generateSteps + [
            "!os.rename('pandoc.out', 'resume.txt')"
        ]
    )
    gen.generate(output=["resume.txt"], copyTempFolder=copyTempFolder)
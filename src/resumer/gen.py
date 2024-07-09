
from contextlib import contextmanager
from dataclasses import dataclass
import os
import shutil
import typing
from resumer.model import Combined
import tempfile
from zrcl.file import FolderWatcher
from .utils import pandoc_generate_file_from_data

_files_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")

@dataclass
class GenPlace:
    dfiles : bool = False

    @classmethod
    def fromDict(cls,data : dict = None,  **kwargs):
        data = data or kwargs
        return cls(**{k : v for k , v in data.items() if k in cls.__dataclass_fields__})

    def __post_init__(self) -> None:
        # create temp directory
        self.tempDir = tempfile.TemporaryDirectory()
        self.__copied = []


    def ensureFile(self, path : str):
        if os.path.exists(path):
            pass
        elif os.path.exists(os.path.join(_files_folder, path)):
            path = os.path.join(_files_folder, path)
        
        shutil.copy(path, os.path.join(self.tempDir.name, os.path.basename(path)))

    def copyFile(self, *files : typing.List[str], target_folder = ""):
        for file in files:
            file: str
            if file.startswith("."):
                for rfile in self.watcher.modified + self.watcher.created:
                    if rfile in self.__copied:
                        continue
                    if rfile.endswith(file) or file == ".":
                        shutil.copy(rfile, os.path.join(os.getcwd(), target_folder, os.path.basename(rfile)))
                        self.__copied.append(rfile)

            else:
                if os.path.join(self.tempDir.name, file) in self.__copied:
                    continue
                shutil.copy(os.path.join(self.tempDir.name, file), os.path.join(os.getcwd(), target_folder, file))
                self.__copied.append(os.path.join(self.tempDir.name, file))

    @contextmanager
    def process(self):
        try:
            self.watcher = FolderWatcher(self.tempDir.name)
            self.cwd = os.getcwd()
            os.chdir(self.tempDir.name)

            yield
        finally:
            os.chdir(self.cwd)
            self.watcher.track_changes()


    def cleanup(self):
        if self.dfiles:
            os.makedirs("resumer_workplace", exist_ok=True)
            self.copyFile(".", target_folder="resumer_workplace")

        self.tempDir.cleanup()

    @staticmethod
    def profile_tex_1(data : Combined, **kwargs):
        gen = GenPlace.fromDict(**kwargs)
        with gen.process():
            pandoc_generate_file_from_data(
                outname="out.tex", 
                template=os.path.join(_files_folder, "tex_1.tex"),
                data=data,
                outtype="latex"
            )
            os.system(f'xelatex out.tex -interaction=nonstopmode -include-directory="{_files_folder}"')

        gen.copyFile(".pdf")
        if os.path.exists("resume.pdf"):
            os.remove("resume.pdf")
        os.rename("out.pdf", "resume.pdf")

        gen.cleanup()
    
    @staticmethod
    def profile_txt_1(data : Combined, **kwargs):
        gen = GenPlace.fromDict(**kwargs)
        with gen.process():
            pandoc_generate_file_from_data(
                outtype="markdown", 
                template=os.path.join(_files_folder, "txt_1.txt"),
                data=data,
                outname="resume.txt"
            )

        gen.copyFile(".txt")
        gen.cleanup()

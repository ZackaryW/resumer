
from dataclasses import dataclass, field
from functools import cached_property
import os
import shutil
import typing
import tempfile
import toml
import yaml

from resumer.core.entry import EntryModel

_data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

default_entries = {
    "qual" : EntryModel(
        fields = ["title", "items"],
        pinned="differs",
    ),
    "exp" : EntryModel(
        fields = ["position", "organization", "location", "datestart", "dateend"],
    ),
    "edu" : EntryModel(
        fields = ["degree", "institution", "location", "datestart", "dateend"],
    ),
    "project" : EntryModel(
        fields = ["name", "position", "location", "datestart", "dateend"],
    ),
}

default_gen_steps = [
    "@createYamlMD",
    "!self._pandocCommand",
]

@dataclass
class Generator:
    ensuringFiles : typing.List[str] = field(default_factory=list)
    entries : typing.Dict[str, EntryModel] = field(default_factory=lambda: default_entries)
    pandocTemplate : str | None = None
    generateSteps : typing.List[str] = field(default_factory=lambda:default_gen_steps)
    @property
    def _outType(self):
        assert self.__pandocTemplate
        if self.__pandocTemplate.endswith(".txt"):
            return "plain"
        elif self.__pandocTemplate.endswith(".md"):
            return "markdown"
        elif self.__pandocTemplate.endswith(".tex"):
            return "latex"
        
        raise ValueError(f"Unsupported file type: {self.__pandocTemplate}")

    @property
    def _pandocCommand(self):
        return "pandoc input.md -o pandoc.out -f markdown -t {outtype} --template={template}".format(
            template=self.__pandocTemplate, outtype=self._outType
        )

    @property
    def __pandocTemplate(self):
        if not self.pandocTemplate:
            if not self.ensuringFiles:
                return None
            return self.ensuringFiles[0]

        return self.pandocTemplate

    @cached_property
    def _rawData(self) -> dict:
        with open(os.path.join(os.getcwd(), 'data.toml'), 'r') as f:
            return toml.load(f)

    @cached_property
    def _entriesData(self):
        ret = {}
        for k, v in self._rawData.items():
            if k not in self.entries:
                continue

            values = []
            pinned = []
            for x in v:
                if "pinned" in x and x["pinned"]:
                    pinned.append(x)
                else:
                    values.append(x)
            ret[k] = {
                "values" : values,
                "pinned" : pinned
            }

            if not ret[k]["pinned"]:
                ret[k].pop("pinned")
        
        return ret

    @cached_property
    def _vars_data(self):
        res = {}
        for k, v in self._rawData.items():
            if k not in self.entries:
                res[k] = v

        return res
    
    @cached_property
    def _data(self) -> dict:
        d = dict(self._vars_data)
        d.update(self._entriesData)
        return d

    @cached_property
    def _tempDir(self) -> tempfile.TemporaryDirectory:
        return tempfile.TemporaryDirectory()
    
    def ensureFile(self, path : str):
        if os.path.exists(os.path.join(_data_folder, path)):
            path = os.path.join(_data_folder, path)

        shutil.copy(path, os.path.join(self._tempDir.name, os.path.basename(path)))

    def createYamlMD(self):
        with open('input.md', 'w') as f:
            f.write("---\n")
            yaml.dump(self._data, f, default_flow_style=False, width=float('inf'))
            
            f.write("---\n")

    def _generate(self, output : typing.List[str], copyTempFolder : bool = False):
        # check if any output files already exist
        if os.path.exists("resumerBkup"):
            shutil.rmtree("resumerBkup")

        for f in output:
            if not os.path.exists(f):
                continue
            os.makedirs("resumerBkup", exist_ok=True)
            shutil.move(os.path.join(os.getcwd(), f), os.path.join("resumerBkup", f))

        # make sure data is generated
        self._data
        # change cwd
        bkupCwd = os.getcwd()
        os.chdir(self._tempDir.name)

        # ensure files
        for f in self.ensuringFiles:
            self.ensureFile(f)

        generateSteps = self.generateSteps.copy()
        while generateSteps:
            cmd = generateSteps.pop(0)
            if cmd.startswith("@"):
                getattr(self, cmd[1:])()
            elif cmd.startswith("!"):
                val = eval(cmd[1:], globals(), locals())
                if val:
                    generateSteps.insert(0, val)
            else:
                os.system(cmd)

        # bring back cwd
        os.chdir(bkupCwd)

        # copy over output
        for f in os.listdir(self._tempDir.name):
            if f not in output:
                continue
            shutil.move(os.path.join(self._tempDir.name, f), os.path.join(bkupCwd, f))
        
        if copyTempFolder:
            shutil.rmtree("resumerOutput", ignore_errors=True)            
            shutil.copytree(self._tempDir.name, "resumerOutput")

        

    def generate(self, output : typing.List[str] = [], copyTempFolder : bool = False):
        try:
            self._generate(output, copyTempFolder)
        except Exception as e:
            # clean up temp folder
            raise e
        finally:
            self._tempDir.cleanup()
            
            # purge __dict__ to only __dataclass_fields__
            self.__dict__ = {k: v for k, v in self.__dict__.items() if k in self.__dataclass_fields__}
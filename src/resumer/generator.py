
import os
import shutil
from typing import overload
import typing
from resumer.model import ResumerData
from resumer.utils import loadFile, yamlToMd


class Generator:
    def __init__(self, data : ResumerData) -> None:
        self.__data = data
        self.__stepExclusion = None

    @overload
    def runstep(self, key : str):
        ...

    @overload
    def runstep(self, step :dict):
        ...

    def runstep(self, step : typing.Union[str, dict]): # type: ignore
        if isinstance(step, str):
            for stepd in self.__data.meta["generate"]["step"]:
                if "name" not in step and step == stepd["cmd"]:
                    self.runstep(stepd)
                elif stepd["name"] == step:
                    self.runstep(stepd)
            raise ValueError(f"step {step} not found")
        else:
            cmd = step.get("cmd", "")
            if cmd:
                cmd += " "
                cmd += " ".join([str(x) for x in step.get("args", [])])
                os.system(cmd)

            if "rename" in step:
                if os.path.exists(step["rename"]):
                    os.remove(step["rename"])
                os.rename(step["input"], step["rename"])

                self.__stepExclusion = step["rename"]

    def run(self):
        # clean temp folder
        if os.path.exists("temp"):
            shutil.rmtree("temp")

        # take a snapshot of the working folder
        currentFiles = os.listdir()

        # create yaml dump file
        gathered ={k : v.dump() for k, v in self.__data.entries.items()}
        gathered.update(self.__data.keydata)
        yamlToMd(gathered)

        # copy overs
        copyover = self.__data.meta["generate"].get("copyover", [])
        for x in copyover:
            if os.path.exists(x):
                continue
            with open(x, "w") as f:
                f.write(loadFile(x)) # type: ignore
            
        # create template file
        outtype = self.__data.meta["generate"].get("outtype")
        
        if outtype == "latex":
            outext = "tex"
        else:
            outext = self.__data.meta["generate"].get("outext", outtype)
        
        templateGen = self.__data.meta["generate"].get("templateGen", f"template.{outext}")

        with open(templateGen, "w") as f:
            f.writelines([x + "\n" for x in self.__data.document])

        # run pandoc
        os.system(f'pandoc input.md -o "pandoc.out" -f markdown -t {outtype} --template={templateGen}')

        # run generate steps
        for step in self.__data.meta["generate"].get("step", []):
            self.runstep(step)

        # make temp folder
        os.makedirs("temp", exist_ok=True)

        # move all files that are created after current files
        for x in os.listdir():
            if not os.path.isfile(x):
                continue
            if x in currentFiles:
                continue
            if x in self.__data.meta["generate"].get("copyover", []):
                continue
            if x == self.__stepExclusion:
                continue
    
            shutil.move(x, f"temp/{x}")

    
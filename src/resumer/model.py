from dataclasses import dataclass, field
import typing
from resumer.utils import checkType, loadFile, builtinStructNames

class BuildSetup(typing.TypedDict):
    values : list
    format : str

class BuildParse(typing.TypedDict):
    top : typing.List[str]
    topText : typing.Union[typing.List[str], str]

    format : str

    footer : typing.List[str]
    footerText : typing.Union[typing.List[str], str]


    setups : typing.Dict[str, typing.Union[BuildSetup, str]]
    

class BuildMeta(typing.TypedDict):
    collection : list
    struct : typing.Dict[str, dict]
    parse : BuildParse
    generate : dict

class Entry(typing.TypedDict):
    pass

class ValueMeta(typing.TypedDict):
    name :str
    title : str
    topbounded : bool
    btmbounded : bool

@dataclass
class EntryItems:
    meta : ValueMeta
    values : typing.List[Entry] = field(default_factory=list)    

    def dump(self):
        return {
            "meta" : self.meta,
            "values" : self.values
        }

@dataclass
class ResumerData:
    meta : BuildMeta
    entries : typing.Dict[str, EntryItems] = field(default_factory=dict)
    document : typing.List[str] = field(default_factory=list)
    keydata : dict = field(default_factory=dict)

    @classmethod
    def loadBuildMeta(cls, datapath : str, rootpath = "default.toml"):
        rootmeta : BuildMeta = loadFile(rootpath)  # type: ignore
        meta : BuildMeta = loadFile(datapath) # type: ignore
        
        if "collection" not in meta:
            meta["collection"] = rootmeta["collection"]

        if "struct" not in meta:
            meta["struct"] = rootmeta["struct"]
        else:
            meta["struct"].update(rootmeta["struct"])

        if "parse" not in meta:
            meta["parse"] = rootmeta["parse"]
        
        if "setups" not in meta["parse"]:
            meta["parse"]["setups"] = rootmeta["parse"]["setups"]
        else:
            meta["parse"]["setups"].update(rootmeta["parse"]["setups"])
    
            for k, v in rootmeta["parse"].items():
                if k == "setups":
                    continue

                if k not in meta["parse"]:
                    meta["parse"][k] = v
                elif isinstance(v, list):
                    meta["parse"][k] = meta["parse"][k] + v
        return meta

    @classmethod
    def generateBaseDocument(cls, parse : BuildParse):
        document = []

        def __internal(a1, a2):
            temp =parse.get(a1, [])
            if temp:
                for x in temp:
                    x = loadFile(x)
                    if isinstance(x, str):
                        document.extend(x.split("\n"))
            temp =parse.get(a2, [])
            if temp:
                if isinstance(temp, str):
                    document.append(temp)
                else:
                    for x in temp:
                        document.append(x)

        __internal("top", "topText")

        currentMarker = len(document)
        __internal("footer", "footerText")
        
        return document, currentMarker


    @classmethod
    def generateDocument(
        cls,
        entryItem : EntryItems,
        struct : dict,
        parsesetup : typing.Optional[BuildSetup] = None,
        
        dformat : typing.Optional[str] = None
    ) -> typing.List[str]:
        template = loadFile(dformat)        
        assert isinstance(template, str)
        
        if not parsesetup:
            counter = 0
            for o in struct:
                if o in builtinStructNames:
                    continue
                template = template.replace(f"<{counter}>", f"$<item>.values.{o}$")
                counter += 1
        else:
            pendingOrder = [x for x in struct if x not in builtinStructNames]
            for i, val in enumerate(parsesetup["values"]):
                if val == "le":
                    # leave empty
                    template = template.replace(f"<{i}>", "")
                elif val == "val":
                    # normal
                    curr = pendingOrder.pop(0)
                    template = template.replace(f"<{i}>", f"$<item>.values.{curr}$")
                elif val == "sv":
                    # skip value
                    curr = pendingOrder.pop(0)
                    template = template.replace(f"<{i}>", "")
                else:
                    template = template.replace(f"<{i}>", f"$<item>.{val}$")
                

        template = template.replace("<item>", entryItem.meta["name"])

        ret = template.splitlines()
        return ret

    @classmethod
    def generateEntryItem(
        cls,
        name : str,
        data : typing.List[dict],
        struct : typing.Optional[dict]
    )-> typing.List[EntryItems]:
        title = struct.get("alias", name) if struct else name
        title = title.capitalize()

        def _create_entry(__item):
            if not struct:
                return Entry(**__item)
            
            __item = Entry(**{x : y for x, y in __item.items() if x in struct})
            checkType(__item, struct) # type: ignore
            return __item

        ret = []
        pinnedlist = []
        entries = []
        for w in data:
            pinned = w.pop("pinned", False)
            if pinned:
                pinnedlist.append(w)
                continue

            entry = _create_entry(w)
            entries.append(entry)

        if pinnedlist:
            pinnedentries = [_create_entry(item) for item in pinnedlist]
            ret.append(
                EntryItems(
                    meta={
                        "name" : f"pinned_{name}",
                        "title" : title,
                        "topbounded" : True,
                        "btmbounded" : True if len(entries) == 0 else False,
                    },
                    values=pinnedentries
                )
            )
        
        if entries:
            ret.append(
                EntryItems(
                    meta={
                        "name" : name,
                        "title" : title,
                        "topbounded" : False if len(pinnedlist) > 0 else True,
                        "btmbounded" : True
                    },
                    values=entries
                )
            )
        return ret

    @classmethod
    def load(cls, datapath : str, configpath : str, skipDoc : bool = False):
        configpath = configpath + ".toml" if not configpath.endswith(".toml") else configpath
        meta = cls.loadBuildMeta(configpath)
        data  = loadFile(datapath)
        assert isinstance(data, dict)
        
        if not skipDoc:
            document, docinsert = cls.generateBaseDocument(meta["parse"])
            newGenDoc = []

        keydata = {
            k : v for k, v in data.items() if k not in meta["collection"]
        }

        entries : typing.List[EntryItems] = []
        for c in meta["collection"]:
            rawlist = data.get(c, [])
            if isinstance(rawlist, dict):
                rawlist = [rawlist]

            generatedEntries = cls.generateEntryItem(
                c,rawlist, meta["struct"].get(c, None)
            )

            if skipDoc:
                continue

            for x in generatedEntries:
                parsesetup = meta["parse"]["setups"].get(x.meta["name"], None)
                if isinstance(parsesetup, str):
                    parsesetup = meta["parse"]["setups"][parsesetup]
                    assert isinstance(parsesetup, dict)
                    dformat = parsesetup.get("format", meta["parse"]["format"])
                else:
                    dformat = meta["parse"]["format"]
                struct = meta["struct"].get(c)
                assert isinstance(struct, dict)
                newGenDoc.extend(cls.generateDocument(x, struct,parsesetup, dformat))

            entries.extend(
                generatedEntries
            )

        entriesdict = {x.meta["name"] : x for x in entries}
        if skipDoc:
            return cls(meta, entriesdict, [], keydata)
        else:
            document = document[:docinsert] + newGenDoc + document[docinsert:]
            return cls(meta, entriesdict, document, keydata)

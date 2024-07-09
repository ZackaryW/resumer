import copy
from dataclasses import dataclass, field, fields, asdict as _asdict
import typing


@dataclass(slots=True)
class Info:
    address : str = None
    city : str = None 
    province : str = None
    country : str = None
    postalcode : str = None

    firstname : str = None
    lastname : str = None
    middlename : str = None
    middleinitial : str = None

    phonenum : str = None
    email : str = None
    linkedin : str = None
    github : str = None
 
    summary : str = None

@dataclass(slots=True)
class CoreComp:
    items : typing.List[str] = field(default_factory=list)



@dataclass(slots=True)
class Entry:
    pinned : bool = False
    order : int = None
    before : str = None
    after : str = None


def asdict(obj):
    return {k : v for k, v in _asdict(obj).items() if k not in fields(Entry)}

@dataclass(slots=True)
class TopQual:
    items : typing.List[str] = field(default_factory=list)


@dataclass(slots=True)
class Qual(Entry):
    title : str = field(default_factory=str)
    items : typing.List[str] = field(default_factory=list)


@dataclass(slots=True)
class Exp(Entry):
    position :str = field(default_factory=str)
    organization : str = field(default_factory=str)
    location : str = field(default_factory=str)
    datestart : str = field(default_factory=str)
    dateend : str = field(default_factory=str)
    items : typing.List[str] = field(default_factory=list)

@dataclass(slots=True)
class Edu(Entry):
    degree : str = field(default_factory=str)
    institution : str = field(default_factory=str)
    location : str = field(default_factory=str)
    datestart : str = field(default_factory=str)
    dateend : str = field(default_factory=str)
    items : typing.List[str] = field(default_factory=list)

@dataclass(slots=True)
class Project(Entry):
    position :str = field(default_factory=str)
    type : str = field(default_factory=str)
    name : str = field(default_factory=str)
    items : typing.List[str] = field(default_factory=list)
    datestart : str = field(default_factory=str)
    dateend : str = field(default_factory=str)
    location : str = field(default_factory=str)

@dataclass(slots=True)
class Combined:
    info : Info
    core : CoreComp
    topqual : TopQual
    exp : typing.List[Exp]
    edu : typing.List[Edu]
    projects : typing.List[Project]
    qual : typing.List[Qual]

    def __merge_list(self, lista, listb):
        """
        Merges two lists, `lista` and `listb`, and returns the merged list. The merging process involves handling special characters in `listb` to modify the behavior of the merge.

        Parameters:
            lista (list): The first list to be merged.
            listb (list): The second list to be merged.

        Returns:
            list: The merged list.

        Special Characters:
            - "-" at the beginning of an item in `listb` indicates that the corresponding item in `lista` should be removed.
            - "[" followed by a number and ":" followed by another number and "]" in an item in `listb` indicates that the items in `lista` at the specified indices should be replaced with the corresponding item in `listb`.
            - "[" followed by a number and "]" in an item in `listb` indicates that the item in `lista` at the specified index should be replaced with the corresponding item in `listb`.

        Example:
            >>> lista = ["apple", "banana", "orange"]
            >>> listb = ["-banana", "[1:2]grape,kiwi", "[0]mango"]
            >>> merged_list = __merge_list(lista, listb)
            >>> print(merged_list)
            ['mango', 'grape', 'kiwi', 'orange']
        """
        minus_query = True
        slicer_specifier = {}

        for i, item in enumerate(listb):
            item : str
            if item.startswith("-"):
                minus_query = True
            elif item.startswith("[") and ":" in item and "]" in item:
                sliced = item[1:].split(":", 1)
                slicer_specifier[int(sliced[0]), int(sliced[1].split("]")[0])] = i
            elif item.startswith("[") and "]" in item:
                slicer_specifier[int(item[1:].split("]")[0])] = i

        if not minus_query and not slicer_specifier:
            lista = list(set(lista + listb))

        # parse slicer   
        copied_listb = copy.deepcopy(listb)
        for addr, i in slicer_specifier.items():
            if len(addr) == 1:
                lista[addr[0]] = copied_listb[i]
                copied_listb.pop(i)
            else:
                lista[addr[0]:addr[1]] = copied_listb[i]
                copied_listb.pop(i)

        lista.extend(copied_listb)

        # parse minus
        all_minuses = [item for item in listb if item.startswith("-")]
        for item in lista:
            if item in all_minuses:
                lista.remove(item)

        filtered_keys = []
        for minus in all_minuses:
            minus = minus[1:]
            if "," in minus:
                filtered_keys.extend(minus.split(","))
            else:
                filtered_keys.append(minus)
            
        pending = []
        for i in len(lista):
            if any(key in lista[i] for key in filtered_keys):
                pending.append(i)

        pending = sorted(pending, reverse=True)

        for i in pending:
            lista.pop(i)

    def __merge_entry(self, entries : typing.List[Exp | Edu], others : typing.List[Exp | Edu]):
        """
        Merge entries from `entries` and `others` lists.

        Args:
            entries (List[Exp | Edu]): The list of entries to merge.
            others (List[Exp | Edu]): The list of entries to merge with.

        Returns:
            None

        This function merges entries from the `entries` and `others` lists. It iterates over each entry in `entries` and checks if it is already parsed. If not, it iterates over each other entry in `others` and compares their attributes. If the count of matching attributes is greater than 2, it merges the lists of items and merges the other attributes of `other` into `entry`. If the count is less than or equal to 2, it adds `entry` to the `unparsed` set. Finally, it extends `entries` with the elements of `unparsed`.
        """
        parsed = []
        unparsed = set()
        for entry in entries:
            for other in others:
                if other in parsed:
                    continue

                count = 0
                for k in fields(other):

                    if getattr(other, k.name) == getattr(entry, k.name):
                        count += 1

                    if count > 2:
                        break

                if count > 2:
                    self.__merge_list(entry.items, other.items)

                    # merge other fields to entry
                    for k in fields(other):
                        if k.name == "items":
                            continue
                        if getattr(other, k.name) is not None:
                            setattr(entry, k.name, getattr(other, k.name))
                    parsed.append(entry)
                else:
                    unparsed.add(entry)

        entries.extend(unparsed)


    def merge(self, other : 'Combined'):
        """
        Merge the contents of another `Combined` object into this object.

        Args:
            other (Combined): The `Combined` object to merge.

        Returns:
            None

        This method merges the contents of another `Combined` object into this object. It merges the information from the `info` attribute of the other object into the `info` attribute of this object. It also merges the items in the `core`, `topqual`, `exp`, `edu`, and `projects` attributes of the other object into the corresponding attributes of this object.

        The merging is done recursively for the `exp` and `edu` attributes, and the `core`, `topqual`, and `projects` attributes are merged using the `__merge_list` method.

        Note:
            - This method modifies the state of this object.
            - The `other` object is not modified.
        """
        # info
        for f in fields(other.info):
            if getattr(other.info, f.name) is not None:
                setattr(self.info, f.name, getattr(other.info, f.name))

        # core
        self.core.items = self.__merge_list(self.core.items, other.core.items)

        # topqual
        self.topqual.items = self.__merge_list(self.topqual.items, other.topqual.items)

        # exp
        self.__merge_entry(self.exp, other.exp)

        # edu
        self.__merge_entry(self.edu, other.edu)

        # project
        self.__merge_entry(self.projects, other.projects)

    @classmethod
    def fromDict(cls, data : dict, parent : 'Combined' = None):
        info = data.get("info", {})
        core = data.get("core", {})
        topqual = data.get("topqual", {})
        exp = data.get("exp", [])
        edu = data.get("edu", [])
        projects = data.get("project", [])
        qual = data.get("qual", [])

        ins = cls(
            info = Info(**info),
            core = CoreComp(**core),
            topqual = TopQual(**topqual),
            exp = [Exp(**e) for e in exp],
            edu = [Edu(**e) for e in edu],
            projects = [Project(**p) for p in projects],
            qual = [Qual(**q) for q in qual],
        )

        if not parent:    
            return ins
    
        parent.merge(ins)
        return parent
        
    def dump_dict(self):
        return {
            "info" : {k : v for k, v in asdict(self.info).items() if v is not None},
            "core" : {k : v for k, v in asdict(self.core).items() if v is not None},
            "topqual" : {k : v for k, v in asdict(self.topqual).items() if v is not None},
            "exp" : [{k : v for k, v in asdict(e).items() if v is not None} for e in self.exp],
            "edu" : [{k : v for k, v in asdict(e).items() if v is not None} for e in self.edu],
            "project" : [{k : v for k, v in asdict(p).items() if v is not None} for p in self.projects],
            "qual" : [{k : v for k, v in asdict(e).items() if v is not None} for e in self.qual],
        }

    
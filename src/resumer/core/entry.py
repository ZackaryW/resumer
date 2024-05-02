
from dataclasses import dataclass, field
import typing


@dataclass(slots=True)
class EntryModel:
    fields : typing.List[str] = field(default_factory=list)
    pinned : typing.Literal["no", "differs", "same"] = "no"
    hasItems : bool = True
    extraMeta : typing.Optional[dict] = None
    extraData : typing.Optional[dict] = None

    

from enum import IntEnum
from .mods import Mods

class CustomModes(IntEnum):
    """An enumeration of the custom modes implemented by the private server."""

    VANILLA = 0
    RELAX = 1
    AUTOPILOT = 2

    def to_db_suffix(self):
        """Returns the database table (for redis and sql) suffix for the given
        `c_mode`."""

        return _db_suffixes[self.value]
    
    @classmethod
    def from_mods(self, mods: Mods) -> 'CustomModes':
        """Creates an instance of `CustomModes` from a mod combo."""

        if mods & Mods.AUTOPILOT: return CustomModes(CustomModes.AUTOPILOT)
        elif mods & Mods.RELAX: return CustomModes(CustomModes.RELAX)
        return CustomModes(CustomModes.VANILLA)

    @property
    def uses_ppboard(self) -> bool:
        """Bool corresponding to whether the c_mode offers pp leaderboards
        by default."""

        return self.value in _uses_ppboard
    
    @property
    def db_table(self) -> str:
        """Returns the MySQL database table for the scores of this `c_mode`."""

        return "scores" + self.to_db_suffix()

_db_suffixes = {
    CustomModes.VANILLA: "",
    CustomModes.RELAX: "_relax",
    CustomModes.AUTOPILOT: "_ap"
}

_uses_ppboard = (
    CustomModes.RELAX,
    CustomModes.AUTOPILOT,
)
from __future__ import annotations

from enum import IntFlag


class Mods(IntFlag):
    NOMOD = 0
    NOFAIL = 1 << 0
    EASY = 1 << 1
    TOUCHSCREEN = 1 << 2
    HIDDEN = 1 << 3
    HARDROCK = 1 << 4
    SUDDENDEATH = 1 << 5
    DOUBLETIME = 1 << 6
    RELAX = 1 << 7
    HALFTIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    AUTOPLAY = 1 << 11
    SPUNOUT = 1 << 12
    AUTOPILOT = 1 << 13
    PERFECT = 1 << 14
    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    FADEIN = 1 << 20
    RANDOM = 1 << 21
    CINEMA = 1 << 22
    TARGET = 1 << 23
    KEY9 = 1 << 24
    KEYCOOP = 1 << 25
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28
    SCOREV2 = 1 << 29
    MIRROR = 1 << 30

    SPEED_MODS = DOUBLETIME | NIGHTCORE | HALFTIME
    GAME_CHANGING = RELAX | AUTOPILOT

    UNRANKED = SCOREV2 | AUTOPLAY | TARGET

    def __repr__(self) -> str:
        if not self.value:
            return "NM"

        _str = ""

        for mod in Mods:
            if self.value & mod and (m := str_mods.get(mod)):
                _str += m

        if self.value & Mods.NIGHTCORE:
            _str = _str.replace("DT", "")
        if self.value & Mods.PERFECT:
            _str = _str.replace("SD", "")

        return _str

    @classmethod
    def convert_str(cls, mods: str) -> Mods:
        _mods = cls.NOMOD  # in case theres none to match

        if not mods or mods == "NM":
            return _mods

        split_mods = [mods[char : char + 2].upper() for char in range(0, len(mods), 2)]

        for mod in split_mods:
            if mod not in mods_str:
                continue

            _mods |= mods_str[mod]

        return _mods

    KEY_MODS = KEY1 | KEY2 | KEY3 | KEY4 | KEY5 | KEY6 | KEY7 | KEY8 | KEY9
    MANIA_ONLY = FADEIN | RANDOM | KEY_MODS
    STD_ONLY = SPUNOUT | AUTOPILOT

    @property
    def conflict(self) -> bool:
        """Anticheat measure to check for illegal mod combos."""

        # Speed mods
        if self & Mods.DOUBLETIME and self & Mods.HALFTIME:
            return True
        if self & Mods.NIGHTCORE and not self & Mods.DOUBLETIME:
            return True

        # Difficulty mods
        if self & Mods.EASY and self & Mods.HARDROCK:
            return True

        # Visibility mods
        if self & Mods.HIDDEN and self & Mods.FADEIN:
            return True

        # Game-changing mods
        if self & Mods.RELAX and self & Mods.AUTOPILOT:
            return True

        # Fail-prevention conflicts
        fail_prevention_mods = Mods.NOFAIL | Mods.RELAX | Mods.AUTOPILOT
        if self & fail_prevention_mods:
            # NF/RX/AP + SD (can't both prevent and require fail)
            if self & Mods.SUDDENDEATH:
                return True
            # NF/RX/AP + PF (can't both allow failure and require perfection)
            if self & Mods.PERFECT:
                return True

        # RX/AP + NF (NF is redundant with RX/AP)
        if self & (Mods.RELAX | Mods.AUTOPILOT):
            if self & Mods.NOFAIL:
                return True

        # SD + PF (PF is stricter, having both is redundant/conflicting)
        if self & Mods.SUDDENDEATH and self & Mods.PERFECT:
            return True

        # SpunOut conflicts with auto-aim mods
        if self & Mods.SPUNOUT:
            if self & (Mods.RELAX | Mods.AUTOPILOT):
                return True

        # Multiple key mods (mania)
        if bin(self & Mods.KEY_MODS).count("1") > 1:
            return True

        return False

    def incompatible_with_mode(self, mode_vn: int) -> bool:
        """Check if mods are incompatible with the given game mode.

        Args:
            mode_vn: Vanilla mode (0=std, 1=taiko, 2=catch, 3=mania)

        Returns:
            True if mods contain mode-incompatible mods
        """
        # Mania-only mods
        if mode_vn != 3 and self & Mods.MANIA_ONLY:
            return True

        # Standard-only mods
        if mode_vn != 0 and self & Mods.STD_ONLY:
            return True

        return False


str_mods = {
    Mods.NOFAIL: "NF",
    Mods.EASY: "EZ",
    Mods.TOUCHSCREEN: "TD",
    Mods.HIDDEN: "HD",
    Mods.HARDROCK: "HR",
    Mods.SUDDENDEATH: "SD",
    Mods.DOUBLETIME: "DT",
    Mods.RELAX: "RX",
    Mods.HALFTIME: "HT",
    Mods.NIGHTCORE: "NC",
    Mods.FLASHLIGHT: "FL",
    Mods.AUTOPLAY: "AU",
    Mods.SPUNOUT: "SO",
    Mods.AUTOPILOT: "AP",
    Mods.PERFECT: "PF",
    Mods.FADEIN: "FI",
    Mods.RANDOM: "RN",
    Mods.CINEMA: "CN",
    Mods.TARGET: "TP",
    Mods.SCOREV2: "V2",
    Mods.MIRROR: "MR",
    Mods.KEY1: "1K",
    Mods.KEY2: "2K",
    Mods.KEY3: "3K",
    Mods.KEY4: "4K",
    Mods.KEY5: "5K",
    Mods.KEY6: "6K",
    Mods.KEY7: "7K",
    Mods.KEY8: "8K",
    Mods.KEY9: "9K",
    Mods.KEYCOOP: "CO",
}

mods_str = {
    "NF": Mods.NOFAIL,
    "EZ": Mods.EASY,
    "TD": Mods.TOUCHSCREEN,
    "HD": Mods.HIDDEN,
    "HR": Mods.HARDROCK,
    "SD": Mods.SUDDENDEATH,
    "DT": Mods.DOUBLETIME,
    "RX": Mods.RELAX,
    "HT": Mods.HALFTIME,
    "NC": Mods.NIGHTCORE,
    "FL": Mods.FLASHLIGHT,
    "AU": Mods.AUTOPLAY,
    "SO": Mods.SPUNOUT,
    "AP": Mods.AUTOPILOT,
    "PF": Mods.PERFECT,
    "FI": Mods.FADEIN,
    "RN": Mods.RANDOM,
    "CN": Mods.CINEMA,
    "TP": Mods.TARGET,
    "V2": Mods.SCOREV2,
    "MR": Mods.MIRROR,
    "1K": Mods.KEY1,
    "2K": Mods.KEY2,
    "3K": Mods.KEY3,
    "4K": Mods.KEY4,
    "5K": Mods.KEY5,
    "6K": Mods.KEY6,
    "7K": Mods.KEY7,
    "8K": Mods.KEY8,
    "9K": Mods.KEY9,
    "CO": Mods.KEYCOOP,
}

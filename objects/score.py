from dataclasses import dataclass
from helpers.discord import log_first_place
from helpers.pep import announce
from helpers.user import safe_name
from typing import Optional
from logger import debug, warning
from consts.modes import Mode
from consts.mods import Mods
from consts.c_modes import CustomModes
from consts.complete import Completed
from consts.privileges import Privileges
from objects.beatmap import Beatmap
from globs.conn import sql
from globs import caches
from libs.crypt import validate_md5
from libs.time import get_timestamp
from lenhttp import Request
from py3rijndael import RijndaelCbc, ZeroPadding
from config import conf
import base64

# PP Calculators
from pp.main import select_calculator

@dataclass
class Score:
    """A class representing a singular score set on a beatmap."""

    id: int
    bmap: Beatmap
    user_id: int
    score: int
    max_combo: int
    full_combo: bool
    passed: bool
    quit: bool
    mods: Mods
    c_mode: CustomModes
    count_300: int
    count_100: int
    count_50: int
    count_katu: int
    count_geki: int
    count_miss: int
    timestamp: int
    mode: Mode
    completed: Completed
    accuracy: float
    pp: float
    play_time: int
    placement: int
    grade: str
    sr: float
    username: str

    @property
    def is_submitted(self) -> bool:
        """Bool corresponding to whether the score has been submitted."""

        return self.id != 0
    
    @classmethod
    async def from_score_sub(self, req: Request) -> Optional['Score']:
        """Creates an instance of `Score` from data provided in a score
        submit request."""

        aes = RijndaelCbc(
            key= "osu!-scoreburgr---------" + req.post_args["osuver"],
            iv= base64.b64decode(req.post_args["iv"]).decode("latin_1"),
            padding= ZeroPadding(32),
            block_size= 32,
        )
        score_data = aes.decrypt(
            base64.b64decode(req.post_args["score"]).decode("latin_1")
        ).decode().split(":")

        # Set data from the score sub.
        map_md5 = score_data[0]

        # Verify map.
        if not validate_md5(map_md5):
            warning(f"Score submit provided invalid beatmap md5 ({map_md5})! "
                    "Giving up.")
            return
        
        # Verify score data sent is correct.
        if len(score_data) != 18: # Not sure if we restrict for this
            warning(f"Someone sent over incorrect score data.... Giving up.")
            return
        
        username = score_data[1].rstrip()
        user_id = await caches.name.id_from_safe(safe_name(username))
        bmap = await Beatmap.from_md5(map_md5)
        mods = Mods(int(score_data[13]))

        s = Score(
            0, bmap, user_id,
            int(score_data[9]),
            int(score_data[10]),
            score_data[11] == "True",
            score_data[14] == "True",
            req.post_args.get("x") == "1",
            mods,
            CustomModes.from_mods(mods),
            int(score_data[3]),
            int(score_data[4]),
            int(score_data[5]),
            int(score_data[7]),
            int(score_data[6]),
            int(score_data[8]),
            get_timestamp(),
            Mode(int(score_data[15])),
            None,
            0.0,
            0.0,
            0, # TODO: Playtime
            0,
            score_data[12],
            0.0,
            username
        )

        s.calc_accuracy()

        return s
    
    async def calc_completed(self) -> Completed:
        """Calculated the `complete` attribute for scores.
        
        Note:
            This DOES update the data for other scores. Only perform this
                function IF you are absolutely certain that this score is
                going to be added to the database.
            Running first place first is recommended for a potential perf
                save.
        """

        debug("Calculating completed.")

        # Get the simple ones out the way.
        if self.placement == 1:
            self.completed = Completed.BEST
            return self.completed
        elif self.quit:
            self.completed = Completed.QUIT
            return self.completed
        elif not self.passed:
            self.completed = Completed.FAILED
            return self.completed
        
        # Don't bother for non-lb things.
        if not self.bmap.has_leaderboard:
            self.completed = Completed.COMPLETE
            return self.completed
        
        table = self.c_mode.db_table
        scoring = "pp" if self.c_mode.uses_ppboard else "score"
        val = self.pp if self.c_mode.uses_ppboard else self.score

        debug("Using MySQL to calculate Completed.")

        query = (
            f"userid = %s AND completed = {Completed.BEST.value} AND beatmap_md5 = %s "
            f"AND play_mode = {self.mode.value}"
        )
        args = (self.user_id, self.bmap.md5,)
        
        # TODO: Set old best to mod best etc
        await sql.execute(
            f"UPDATE {table} SET completed = {Completed.COMPLETE.value} WHERE "
            + query + f" AND {scoring} < {val} LIMIT 1", args
        )

        # Check if it remains.
        ex_db = await sql.fetchcol(
            f"SELECT 1 FROM {table} WHERE " + query + " LIMIT 1",
            (self.user_id, self.bmap.md5)
        )

        if not ex_db:
            self.completed = Completed.BEST
            return self.completed
        
        # Now we check for mod bests.
        await sql.execute(
            f"UPDATE {table} SET completed = {Completed.COMPLETE.value} WHERE "
            f"completed = {Completed.MOD_BEST.value} AND userid = %s AND "
            f"play_mode = {self.mode.value} AND beatmap_md5 = %s AND mods = %s "
            f"AND {scoring} < %s LIMIT 1", (self.user_id, self.bmap.md5,
            self.mods.value, val)
        )

        mod_ex_db = await sql.fetchcol(
            f"SELECT 1 FROM {table} WHERE mods = %s AND play_mode = %s AND "
            "userid = %s AND beatmap_md5 = %s AND mods = %s AND "
            f"completed = {Completed.MOD_BEST.value} LIMIT 1",
            (self.mods.value, self.mode.value, self.user_id, self.bmap.md5,
            self.mods.value)
        )

        if mod_ex_db:
            debug("Calculated simple completed.")
            self.completed = Completed.COMPLETE
            return self.completed
        
        debug("Calculated mod best!")
        self.completed = Completed.MOD_BEST
        return self.completed
    
    async def calc_placement(self) -> int:
        """Calculates the placement of the score on the leaderboards.
        
        Note:
            Performs a generally costly query.
            Returns 0 if bmap ranked status doesnt have lbs.
            Returns 0 if completed doesnt allow.
        """

        if (not self.passed) or (not self.bmap.has_leaderboard):
            debug("Not bothering calculating placement.")
            self.placement = 0
            return 0
        
        debug("Calculating score placement based on MySQL.")

        table = self.c_mode.db_table
        scoring = "pp" if self.c_mode.uses_ppboard else "score"
        val = self.pp if self.c_mode.uses_ppboard else self.score

        self.placement = (await sql.fetchcol(
            f"SELECT COUNT(*) FROM {table} s INNER JOIN users u ON s.userid = "
            f"u.id WHERE u.privileges & {Privileges.USER_PUBLIC.value} AND "
            f"s.play_mode = {self.mode.value} AND s.completed = {Completed.BEST.value} "
            f"AND {scoring} > %s AND s.beatmap_md5 = %s",
            (val, self.bmap.md5)
        )) + 1

        return self.placement
    
    async def calc_pp(self) -> float:
        """Calculates the PP given for the score."""

        if (not self.bmap.has_leaderboard):# or (not self.passed):
            debug("Not bothering to calculate PP.")
            self.pp = .0
            return self.pp
        debug("Calculating PP...") # We calc for failed scores!
        
        # TODO: More calculators (custom for standard.)
        calc = select_calculator(self.mode, self.c_mode).from_score(self)
        self.pp, self.sr = await calc.calculate()
        return self.pp
    
    # This gives me aids looking at it LOL. Copied from old Kisumi
    def calc_accuracy(self) -> float:
        """Calculates the accuracy of the score. Credits to Ripple for this as
        osu! wiki is not working :woozy_face:"""

        acc = .0
        # osu!std
        if self.mode == Mode.STANDARD:
            acc =  (
                (self.count_50*50+self.count_100*100+self.count_300*300)
                / ((self.count_300+self.count_100+self.count_50+self.count_miss) * 300)
            )
        # These may be slightly inaccurate but its the best we have without some next gen calculations.
        # Taiko
        elif self.mode == Mode.TAIKO:
            acc = (
                (self.count_100*50)+(self.count_300*100))/(
                (
                    self.count_300+self.count_100+self.count_miss
                ) * 100
            )
        # Catch the beat
        elif self.mode == Mode.CATCH:
            acc = (
                (self.count_300+self.count_100+self.count_50)
                / (self.count_300+self.count_100+self.count_50+self.count_miss+self.count_katu)
            )
        # Mania
        elif self.mode == Mode.MANIA:
            acc = (
                (
                    self.count_50*50+self.count_100*100+self.count_katu*200+self.count_300*300+self.count_geki*300
                ) / (
                    (self.count_miss+self.count_50+self.count_100+self.count_300+self.count_geki+self.count_katu) * 300
                )
            )
        
        # I prefer having it as a percentage.
        self.accuracy = acc * 100
        return self.accuracy
    
    async def on_first_place(self) -> None:
        """Adds the score to the first_places table."""

        # Why did I design this system when i was stupid...

        # Delete previous first place.
        await sql.execute(
            "DELETE FROM first_places WHERE beatmap_md5 = %s AND mode = %s AND "
            "relax = %s LIMIT 1",
            (self.bmap.md5, self.mode.value, self.c_mode.value)
        )

        # And now we insert the new one.
        await sql.execute(
            "INSERT INTO first_places (score_id, user_id, score, max_combo, full_combo,"
            "mods, 300_count, 100_count, 50_count, miss_count, timestamp, mode, completed,"
            "accuracy, pp, play_time, beatmap_md5, relax) VALUES "
            "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (self.id, self.user_id, self.score, self.max_combo, self.full_combo,
            self.mods.value, self.count_300, self.count_100, self.count_50, self.count_miss,
            self.timestamp, self.mode.value, self.completed.value, self.accuracy, self.pp,
            self.play_time, self.bmap.md5, self.c_mode.value)
        )
        debug("First place added.")

        # TODO: Move somewhere else.
        msg = (f"[{self.c_mode.acronym}] User [{conf.srv_url}/u/{self.user_id} "
        f"{self.username}] has submitted a #1 place on "
        f"[{conf.srv_url}/beatmaps/{self.bmap.id} {self.bmap.song_name}]"
        f" +{self.mods.readable} ({round(self.pp, 2)}pp)")
        # Announce it.
        await announce(msg)
        await log_first_place(self)

    async def submit(self, clear_lbs: bool = True, calc_completed: bool = True,
                     calc_place: bool = True, calc_pp: bool = True) -> None:
        """Inserts the score into the database, performing other necessary
        calculations.
        
        Args:
            clear_lbs (bool): If true, the leaderboard and personal best
                cache for this beatmap + c_mode + mode combo.
            calc_completed (bool): Whether the `completed` attribute should
                be calculated (MUST NOT BE RAN BEFORE, ELSE SCORES WILL BE
                WEIRD IN THE DB)
            calc_place (bool): Whether the placement of the score should be
                calculated (may not be calculated if `completed` does not
                allow so).
            calc_pp (bool): Whether the PP for the score should be recalculated
                from scratch.
        """

        if calc_pp: await self.calc_pp() # We need this for the rest.
        if calc_completed: await self.calc_completed()
        if clear_lbs and self.completed == Completed.BEST:
            caches.clear_lbs(self.bmap.md5, self.mode, self.c_mode)
            caches.clear_pbs(self.bmap.md5, self.mode, self.c_mode)
        if calc_place: await self.calc_placement()

        await self.__insert()

        # Handle first place.
        if self.placement == 1:
            await self.on_first_place()

    async def __insert(self) -> None:
        """Inserts the score directly into the database. Also assigns the
        `id` attribute to the score ID."""

        table = self.c_mode.db_table
        ts = get_timestamp()

        debug("Inserting score into the MySQL database.")

        self.id = await sql.execute(
            f"INSERT INTO {table} (beatmap_md5, userid, score, max_combo, full_combo, mods, "
            "300_count, 100_count, 50_count, katus_count, gekis_count, misses_count, time, "
            "play_mode, completed, accuracy, pp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            "%s,%s,%s,%s,%s)",
            (self.bmap.md5, self.user_id, self.score, self.max_combo, int(self.full_combo),
            self.mods.value, self.count_300, self.count_100, self.count_50, self.count_katu,
            self.count_geki, self.count_miss, ts, self.mode.value, self.completed.value,
            self.accuracy, self.pp)
        )
    
    async def save_pp(self) -> None:
        """Saves the score PP attribute to the scores table.
        
        Note:
            This does NOT raise an exception if score is not submitted.
        """

        await sql.execute(
            f"UPDATE {self.c_mode.db_table} SET pp = %s WHERE id = %s LIMIT 1",
            (self.pp, self.id)
        )

    @classmethod
    async def from_db(cls, score_id: int, c_mode: CustomModes) -> Optional['Score']:
        """Creates an instance of `Score` using data fetched from the
        database.
        
        Args:
            score_id (int): The ID of the score within the database.
            table (str): The table the score should be loacted within 
                (directly formatted into the query).
        """

        table = c_mode.db_table
        s_db = await sql.fetchone(
            f"SELECT s.*, a.username FROM {table} s INNER JOIN users a "
            "ON s.userid = a.id WHERE id = %s LIMIT 1",
            (score_id,)
        )

        if s_db is None:
            # Score not found in db.
            return None

        bmap = await Beatmap.from_md5(s_db[1])

        s = Score(
            id= s_db[0], 
            bmap= bmap, 
            user_id= s_db[2],
            score= s_db[3], 
            max_combo= s_db[4], 
            full_combo= s_db[5],
            passed= True, 
            quit= False, 
            mods= s_db[6],
            c_mode= c_mode,
            count_300= s_db[7], 
            count_100= s_db[8], 
            count_50= s_db[9], 
            count_katu= s_db[10],
            count_geki= s_db[11], 
            count_miss= s_db[12], 
            timestamp= s_db[13],
            mode= Mode(s_db[14]), 
            completed= Completed(s_db[15]),
            accuracy= s_db[16], 
            pp= s_db[17], 
            play_time= s_db[18], 
            placement= 0, 
            grade= "",
            sr= 0.0,
            username= s_db[19]
        )
        await s.calc_placement(False)

        return s

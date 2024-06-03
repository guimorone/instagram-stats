# Changeble depending on the programmer purpose.
# https://instaloader.github.io/module/instaloadercontext.html#ratecontroller
from instaloader import RateController, InstaloaderContext
from random import randint
from utils.constants import SLEEP_GAP


class InstaloaderRateController(RateController):
    def __init__(self, context: InstaloaderContext, before_query_secs: int = 0) -> None:
        super().__init__(context)
        self.__before_query_secs: int = int(before_query_secs)

    def wait_before_query(self, query_type: str) -> None:
        if self.__before_query_secs <= 0:
            return super().wait_before_query(query_type)

        secs = randint(self.__before_query_secs, self.__before_query_secs + SLEEP_GAP)
        print("Waiting", secs, "seconds for", query_type, "query type")
        print("** This is necessary due to instagram query limitations! **")
        self.sleep(secs)

    def add_before_query_secs(self, secs: int) -> None:
        self.__before_query_secs += int(secs)

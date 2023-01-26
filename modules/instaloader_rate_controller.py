# Changeble depending on the programmer purpose.
# https://instaloader.github.io/module/instaloadercontext.html#ratecontroller
from instaloader import RateController, InstaloaderContext
from random import randint
from time import sleep
from utils.constants import RANDOM_GAP


class InstaloaderRateController(RateController):
    # DEFAULT METHODS
    def __init__(self, context: InstaloaderContext, before_query_secs: int = 0):
        super().__init__(context)
        self.__before_query_secs = int(before_query_secs)

    def sleep(self, secs: float) -> None:
        return super().sleep(secs)

    def count_per_sliding_window(self, query_type: str) -> int:
        return super().count_per_sliding_window(query_type)

    def query_waittime(
        self, query_type: str, current_time: float, untracked_queries: bool = False
    ) -> float:
        return super().query_waittime(query_type, current_time, untracked_queries)

    def wait_before_query(self, query_type: str) -> None:
        if not self.__before_query_secs:
            return super().wait_before_query(query_type)

        secs = randint(self.__before_query_secs, self.__before_query_secs + RANDOM_GAP)
        print("Waiting", secs, "seconds for", query_type, "query type")
        print("** This is necessary due to instagram query limitations! **")
        sleep(secs)

    def handle_429(self, query_type: str) -> None:
        return super().handle_429(query_type)

    # PERSONAL METHODS
    def add_before_query_secs(self, secs: int) -> None:
        self.__before_query_secs += int(secs)

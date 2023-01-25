# Changeble depending on the programmer purpose.
# https://instaloader.github.io/module/instaloadercontext.html#ratecontroller
from instaloader import RateController
from random import randint
from time import sleep


class InstaloaderRateController(RateController):
    def sleep(self, secs: float) -> None:
        return super().sleep(secs)

    def count_per_sliding_window(self, query_type: str) -> int:
        return super().count_per_sliding_window(query_type)

    def query_waittime(
        self, query_type: str, current_time: float, untracked_queries: bool = False
    ) -> float:
        return super().query_waittime(query_type, current_time, untracked_queries)

    def wait_before_query(self, query_type: str) -> None:
        secs = randint(10, 20)
        print("Waiting", secs, "seconds for", query_type, "query type")
        sleep(secs)
        # return super().wait_before_query(query_type)

    def handle_429(self, query_type: str) -> None:
        return super().handle_429(query_type)

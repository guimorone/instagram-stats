from instaloader import RateController


class InstaloaderRateController(RateController):
    def sleep(self, secs: float):
        return super().sleep(secs)

    def count_per_sliding_window(self, query_type: str):
        return super().count_per_sliding_window(query_type)

    def query_waittime(
        self, query_type: str, current_time: float, untracked_queries: bool = False
    ):
        return super().query_waittime(query_type, current_time, untracked_queries)

    def wait_before_query(self, query_type: str):
        super().wait_before_query(query_type)

    def handle_429(self, query_type: str):
        super().handle_429(query_type)

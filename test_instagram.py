import sys
import traceback
import timeit
import logging
import pandas as pd

import instaloader
from instaloader.exceptions import (
    TwoFactorAuthRequiredException,
    ConnectionException,
    BadCredentialsException,
)


class CustomLoggerFormatter(logging.Formatter):

    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;1m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - (%(filename)s:%(lineno)d) - %(levelname)s : %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + format + reset,
        logging.INFO: BLUE + format + reset,
        logging.WARNING: YELLOW + format + reset,
        logging.ERROR: RED + format + reset,
        logging.CRITICAL: BOLD_RED + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLoggerFormatter())

logger.addHandler(ch)


class MyRateController(instaloader.RateController):
    pass


class InstaBot:
    def __init__(self, username: str, password: str):
        start = timeit.default_timer()

        self.__username = username
        self.__password = password
        self.__Loader = instaloader.Instaloader(
            rate_controller=lambda ctx: MyRateController(ctx)
        )

        self.login()
        self.__profile = self.get_profile()
        self.followers = self.get_followers(self.__profile)
        self.followings = self.get_followees(self.__profile)
        self.people_that_do_not_follow_back = self.get_people_that_do_not_follow_back()

        self.debug_numbers(start)
        self.__Loader.close()

    def login(self):
        try:
            logger.info(f"Logging into {self.__username} account...")
            self.__Loader.login(self.__username, self.__password)
        except TwoFactorAuthRequiredException:
            code = input("Verification Code: ")
            while not code:
                logger.error("--- Error while trying to send the verification code ---")
                code = input("Try again: ")
            self.__Loader.two_factor_login(code)
        except (ConnectionException, BadCredentialsException):
            logger.critical(
                "Too many requests of login in this account or invalid credentials, try again later!"
            )
            exit()

    def get_profile(self):
        profile_to_fetch = input(
            "Profile to fetch (skip to fetch the logged account): "
        )
        profile_to_fetch = profile_to_fetch if profile_to_fetch else self.__username
        logger.info(f"Loading {profile_to_fetch} profile from an Instagram handle...")

        return instaloader.Profile.from_username(
            self.__Loader.context, profile_to_fetch
        )

    def get_followers(self, profile: instaloader.Profile):
        logger.info(
            "Retrieving the usernames of all followers and converting to CSV..."
        )

        followers = [follower.username for follower in profile.get_followers()]
        followers_df = pd.DataFrame(followers, columns=["Username"])
        followers_df.to_csv("followers.csv", index=False)

        return followers

    def get_followees(self, profile: instaloader.Profile):
        logger.info(
            "Retrieving the usernames of all followings and converting to CSV..."
        )

        followings = [followee.username for followee in profile.get_followees()]
        followings_df = pd.DataFrame(followings, columns=["Username"])
        followings_df.to_csv("followings.csv", index=False)

        return followings

    def get_people_that_do_not_follow_back(self):
        logger.info(
            "Retrieving the usernames of all people that do not follow back and converting to CSV..."
        )

        people_that_do_not_follow_back = list(
            filter(lambda u: u not in self.followers, self.followings)
        )
        people_that_do_not_follow_back_df = pd.DataFrame(
            people_that_do_not_follow_back, columns=["Username"]
        )
        people_that_do_not_follow_back_df.to_csv(
            "people_that_do_not_follow_back.csv", index=False
        )

        return people_that_do_not_follow_back

    def debug_numbers(self, start: float):
        logger.debug("-------------- NUMBERS --------------")
        logger.debug(f"Followers: {len(self.followers)}")
        logger.debug(f"Followings: {len(self.followings)}")
        logger.debug(
            f"People that do not follow back: {len(self.people_that_do_not_follow_back)}"
        )
        stop = timeit.default_timer()
        logger.debug(f"Runtime: {stop - start} seconds")
        logger.debug("-------------------------------------")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.warning(f"Usage: `python {sys.argv[0]} USERNAME PASSWORD`")
        logger.error("Set your credentials properly and try again!")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        try:
            instance = InstaBot(username, password)
        except:
            traceback.print_exc()

import pandas as pd
import sys
import traceback
import timeit
import instaloader
from instaloader.exceptions import (
    TwoFactorAuthRequiredException,
    ConnectionException,
    BadCredentialsException,
)
from pick import pick
from modules.instaloader_rate_controller import InstaloaderRateController
from utils.misc import setup_logger, get_runtime_text

logger = setup_logger(__name__)


class InstaBot:
    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password
        self.__Loader = instaloader.Instaloader(
            rate_controller=lambda ctx: InstaloaderRateController(ctx)
        )
        self.__profile = None
        self.__followers = []
        self.__followings = []
        self.__people_that_do_not_follow_back = []

        self.__all_methods = {
            "get_followers_stats": {
                "method": self.__get_followers_stats,
                "debug": lambda: (
                    logger.debug(f"Followers: {len(self.__followers)}"),
                    logger.debug(f"Followings: {len(self.__followings)}"),
                    logger.debug(
                        f"People that do not follow back: {len(self.__people_that_do_not_follow_back)}"
                    ),
                ),
            }
        }
        self.__method_applied = ""

    # GETTERS AND SETTERS
    def see_all_methods_as_list(self, upper_names: bool = True):
        return [m.upper() if upper_names else m for m in self.__all_methods.keys()]

    def see_current_method(self):
        return self.__method_applied

    def get_followers_list(self):
        return self.__followers

    def get_followings_list(self):
        return self.__followings

    def get_people_that_do_not_follow_back_list(self):
        return self.__people_that_do_not_follow_back

    # PUBLIC METHODS
    def run(self, method_choose: str):
        if not method_choose:
            return

        self.__start_time = timeit.default_timer()
        self.__method_applied = method_choose
        self.__login()
        try:
            self.__all_methods.get(self.__method_applied).get("method")()
        except:
            logger.critical(f"{self.__method_applied} FAILED TO EXECUTE!")

    def debug_numbers(self, title: str = "NUMBERS"):
        if not self.__method_applied:
            logger.warning("No method was chosen.")
            return

        logger.debug(f"---------------- {title} ----------------")
        try:
            self.__all_methods.get(self.__method_applied).get("debug")()
        except:
            logger.error("Error while trying to print the debug numbers")
        finally:
            end_time = timeit.default_timer()
            logger.debug("-----------------------------------------")
            logger.debug(f"Runtime: {get_runtime_text(self.__start_time, end_time)}")

    def end_session(self, with_debug: bool = True):
        if with_debug:
            self.debug_numbers()
        self.__Loader.close()

    # PRIVATE METHODS
    def __login(self):
        try:
            logger.info(f"Logging into {self.__username} account...")
            self.__Loader.login(self.__username, self.__password)
        except TwoFactorAuthRequiredException:
            code = input("Verification Code: ")
            while not code:
                logger.warning(
                    "--- Error while trying to send the verification code, it seems that it is empty ---"
                )
                code = input("Try again: ")
            self.__Loader.two_factor_login(code)
        except (ConnectionException, BadCredentialsException):
            logger.error(
                "Too many requests of login in this account or invalid credentials, try again later!"
            )
            exit()

    def __get_followers_stats(self):
        self.__profile = self.__get_profile()
        self.__followers = self.__get_followers()
        self.__followings = self.__get_followees()
        self.__people_that_do_not_follow_back = (
            self.__get_people_that_do_not_follow_back()
        )

    def __get_profile(self):
        profile_to_fetch = input(
            "Profile to fetch (skip to fetch the logged account): "
        )
        profile_to_fetch = profile_to_fetch if profile_to_fetch else self.__username
        logger.info(f"Loading {profile_to_fetch} profile from an Instagram handle...")

        return instaloader.Profile.from_username(
            self.__Loader.context, profile_to_fetch
        )

    def __get_followers(self):
        logger.info(
            "Retrieving the usernames of all followers and converting to CSV..."
        )

        followers = [follower.username for follower in self.__profile.get_followers()]
        followers_df = pd.DataFrame(followers, columns=["Username"])
        followers_df.to_csv("followers.csv", index=False)

        return followers

    def __get_followees(self):
        logger.info(
            "Retrieving the usernames of all followings and converting to CSV..."
        )

        followings = [followee.username for followee in self.__profile.get_followees()]
        followings_df = pd.DataFrame(followings, columns=["Username"])
        followings_df.to_csv("followings.csv", index=False)

        return followings

    def __get_people_that_do_not_follow_back(self):
        logger.info(
            "Retrieving the usernames of all people that do not follow back and converting to CSV..."
        )

        people_that_do_not_follow_back = list(
            filter(lambda u: u not in self.__followers, self.__followings)
        )
        people_that_do_not_follow_back_df = pd.DataFrame(
            people_that_do_not_follow_back, columns=["Username"]
        )
        people_that_do_not_follow_back_df.to_csv(
            "people_that_do_not_follow_back.csv", index=False
        )

        return people_that_do_not_follow_back


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.warning(f"Usage: `python {sys.argv[0]} USERNAME PASSWORD`")
        logger.error("Set your credentials properly and try again!")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        instagram_instance = InstaBot(username, password)
        try:
            title = "Please, choose your option: "
            options = instagram_instance.see_all_methods_as_list()
            option, index = pick(options, title, indicator="=>", default_index=0)
            print(f"{index + 1}º", "method chosen:", option, end="\n\n")

            instagram_instance.run(option.lower())
        except:
            traceback.print_exc()
        finally:
            instagram_instance.end_session()

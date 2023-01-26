import pandas as pd
import sys
import traceback
import timeit
import instaloader
from instaloader.exceptions import (
    TwoFactorAuthRequiredException,
    ConnectionException,
    BadCredentialsException,
    InvalidArgumentException,
    ProfileNotExistsException,
)
from pick import pick
from modules.instaloader_rate_controller import InstaloaderRateController
from utils.misc import setup_logger, get_runtime_text
from utils.constants import USERS_LIMIT, SECONDS_TO_ADD

logger = setup_logger(__name__)


class InstaBot:
    def __init__(self, username: str, password: str) -> None:
        self.__username = username
        self.__password = password
        self.__Loader = instaloader.Instaloader(
            rate_controller=lambda ctx: InstaloaderRateController(ctx)
        )
        self.__profile = None
        self.__followers = []
        self.__followings = []
        self.__people_that_do_not_follow_back = []
        self.__similar_accounts = []

        self.__all_methods = {
            "get_followers_stats": {
                "method": self.__get_followers_stats,
                "debug": lambda: (
                    logger.debug(f"Followers: {len(self.__followers)}"),
                    logger.debug(f"Followings: {len(self.__followings)}"),
                    logger.debug(
                        f"People that do not follow back: {len(self.__people_that_do_not_follow_back)}"
                    ),
                    logger.debug(f"Similar accounts: {len(self.__similar_accounts)}"),
                ),
            }
        }
        self.__method_applied = ""

    # GETTERS AND SETTERS
    def see_all_methods_as_list(self, upper_names: bool = True) -> list[str]:
        return [m.upper() if upper_names else m for m in self.__all_methods.keys()]

    def see_current_method(self) -> str:
        return self.__method_applied

    def get_followers_list(self) -> list[str]:
        return self.__followers

    def get_followings_list(self) -> list[str]:
        return self.__followings

    def get_people_that_do_not_follow_back_list(self) -> list[str]:
        return self.__people_that_do_not_follow_back

    def get_similar_accounts_list(self) -> list[str]:
        return self.__similar_accounts

    # PUBLIC METHODS
    def run(self, method_choose: str) -> None:
        if not method_choose:
            return

        self.__start_time = timeit.default_timer()
        self.__method_applied = method_choose
        self.__login()
        try:
            self.__all_methods.get(self.__method_applied).get("method")()
        except:
            logger.critical(f"{self.__method_applied} FAILED TO EXECUTE!")

    def debug_numbers(self, header: str = "NUMBERS") -> None:
        title = header
        if not self.__method_applied:
            logger.warning("No method was chosen.")
            return

        title += " " + self.__method_applied.upper()
        logger.debug(f"---------------- {title} ----------------")
        try:
            self.__all_methods.get(self.__method_applied).get("debug")()
        except:
            logger.error("Error while trying to print the debug numbers")
        finally:
            end_time = timeit.default_timer()
            logger.debug("----------------------------------" + ("-" * len(title)))
            logger.debug(f"Runtime: {get_runtime_text(self.__start_time, end_time)}")

    def end_session(self, with_debug: bool = True) -> None:
        if with_debug:
            self.debug_numbers()
        self.__Loader.close()

    # PRIVATE METHODS
    def __login(self) -> None:
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
        except (
            ConnectionException,
            BadCredentialsException,
            InvalidArgumentException,
        ) as err:
            logger.error(err)
            exit()

    def __rate_controller_add_before_query_secs(self, secs: int) -> None:
        self.__Loader.context._rate_controller.add_before_query_secs(secs)

    def __get_followers_stats(self) -> None:
        self.__profile = self.__get_profile()
        self.__followers = self.__get_followers()
        self.__followings = self.__get_followees()
        self.__people_that_do_not_follow_back = (
            self.__get_people_that_do_not_follow_back()
        )
        self.__similar_accounts = self.__get_similar_accounts()

    def __get_profile(self) -> instaloader.Profile:
        profile = None
        profile_to_fetch = input(
            "Profile to fetch (skip to fetch the logged account): "
        )

        while True:
            profile_to_fetch = profile_to_fetch if profile_to_fetch else self.__username
            logger.info(
                f"Loading {profile_to_fetch} profile from an Instagram handle..."
            )
            try:
                profile = instaloader.Profile.from_username(
                    self.__Loader.context, profile_to_fetch
                )
            except ProfileNotExistsException:
                logger.error("Profile do not exist, try again!")
                profile_to_fetch = input(
                    "Profile to fetch (skip to fetch the logged account): "
                )
            except:
                traceback.print_exc()
            else:
                break

        num_followers = profile.followers
        num_followings = profile.followees
        secs = ((num_followers + num_followings) // USERS_LIMIT) * SECONDS_TO_ADD
        self.__rate_controller_add_before_query_secs(secs)

        return profile

    def __get_followers(self) -> list[str]:
        logger.info(
            "Retrieving the usernames of all followers and converting to CSV..."
        )

        followers = [follower.username for follower in self.__profile.get_followers()]
        followers_df = pd.DataFrame(followers, columns=["Username"])
        followers_df.to_csv("followers.csv", index=False)

        return followers

    def __get_followees(self) -> list[str]:
        logger.info(
            "Retrieving the usernames of all followings and converting to CSV..."
        )

        followings = [followee.username for followee in self.__profile.get_followees()]
        followings_df = pd.DataFrame(followings, columns=["Username"])
        followings_df.to_csv("followings.csv", index=False)

        return followings

    def __get_people_that_do_not_follow_back(self) -> list[str]:
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

    def __get_similar_accounts(self) -> list[str]:
        logger.info(
            "Retrieving the usernames of all similar accounts and converting to CSV..."
        )

        similar_accounts = [sa.username for sa in self.__profile.get_similar_accounts()]
        similar_accounts_df = pd.DataFrame(similar_accounts, columns=["Username"])
        similar_accounts_df.to_csv("simillar_accounts.csv", index=False)

        return similar_accounts


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

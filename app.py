import pandas as pd
import sys
import traceback
import timeit
import time
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
        self.query_wait_time = 20  # seconds
        self.__username = username.strip()
        self.__password = password.strip()
        self.__Loader = instaloader.Instaloader(rate_controller=lambda ctx: InstaloaderRateController(ctx))
        self.__profile = None
        self.profile_to_fetch = ""
        self.__followers = []
        self.__followees = []
        self.__people_that_do_not_follow_back = []
        self.__similar_accounts = []

        self.__all_methods = {
            "get_followers_stats": {
                "method": self.__get_followers_stats,
                "debug": lambda: (
                    logger.debug(f"Followers: {len(self.__followers)}"),
                    logger.debug(f"Followees: {len(self.__followees)}"),
                    logger.debug(f"People that do not follow back: {len(self.__people_that_do_not_follow_back)}"),
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

    def get_followees_list(self) -> list[str]:
        return self.__followees

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
        while True:
            try:
                self.__all_methods.get(self.__method_applied).get("method")()
            except ConnectionException:
                logger.error("Connection expired, logging in again...")
                self.__login()
            except:
                logger.critical(f"{self.__method_applied} FAILED TO EXECUTE!")
                logger.warning(f"Waiting {self.query_wait_time} seconds before trying again.")
                time.sleep(self.query_wait_time)
            else:
                break

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
                logger.warning("--- Error while trying to send the verification code, it seems that it is empty ---")
                code = input("Try again: ")
            self.__Loader.two_factor_login(code)
        except (
            ConnectionException,
            BadCredentialsException,
            InvalidArgumentException,
        ) as err:
            logger.error(err)
            exit()

    # def __rate_controller_add_before_query_secs(self, secs: int) -> None:
    #     self.__Loader.context._rate_controller.add_before_query_secs(secs)

    def __get_followers_stats(self) -> None:
        self.__profile, num_followers, num_followees = self.__get_profile()
        self.__followers = self.__get_followers(num_followers)
        self.__followees = self.__get_followees(num_followees)
        self.__people_that_do_not_follow_back = self.__get_people_that_do_not_follow_back()
        self.__similar_accounts = self.__get_similar_accounts()

    def __get_profile(self) -> tuple[instaloader.Profile, int, int]:
        profile = None
        profile_to_fetch = (
            self.profile_to_fetch
            if self.profile_to_fetch
            else input("Profile to fetch (skip to fetch the logged account): ")
        )

        while True:
            profile_to_fetch = profile_to_fetch.strip() if profile_to_fetch else self.__username
            logger.info(f"Loading {profile_to_fetch} profile from an Instagram handle...")
            try:
                profile = instaloader.Profile.from_username(self.__Loader.context, profile_to_fetch)
            except ProfileNotExistsException:
                logger.error("Profile do not exist, try again!")
                profile_to_fetch = input("Profile to fetch (skip to fetch the logged account): ")
            except Exception as err:
                logger.error(err)
            else:
                break

        self.profile_to_fetch = profile_to_fetch

        num_followers = profile.followers
        num_followees = profile.followees
        # secs = ((num_followers + num_followees) // USERS_LIMIT) * SECONDS_TO_ADD
        # self.__rate_controller_add_before_query_secs(secs)

        return profile, num_followers, num_followees

    def __get_followers(self, num_followers: int) -> list[str]:
        followers = []
        count = 1

        wait_time = self.query_wait_time
        while True:
            wait_time += 10 * (count // 10)
            logger.info(f"{count}º attempt. Retrieving the usernames of all followers and converting to CSV...")
            followers = [follower.username for follower in self.__profile.get_followers()]

            if len(followers) >= num_followers:
                break

            count += 1
            logger.warning(f"Trying again due to Instagram query limitations! Please wait {wait_time} seconds.")
            time.sleep(wait_time)

        followers_df = pd.DataFrame(followers, columns=["Username"])
        followers_df.to_csv("followers.csv", index=False)

        return followers

    def __get_followees(self, num_followees: int) -> list[str]:
        followees = []
        count = 1

        wait_time = self.query_wait_time
        while True:
            wait_time += 10 * (count // 10)
            logger.info(f"{count}º attempt. Retrieving the usernames of all followees and converting to CSV...")
            followees = [followee.username for followee in self.__profile.get_followees()]

            if len(followees) >= num_followees:
                break

            count += 1
            logger.warning(f"Trying again due to Instagram query limitations! Please wait {wait_time} seconds.")
            time.sleep(wait_time)

        followees_df = pd.DataFrame(followees, columns=["Username"])
        followees_df.to_csv("followees.csv", index=False)

        return followees

    def __get_people_that_do_not_follow_back(self) -> list[str]:
        logger.info("Retrieving the usernames of all people that do not follow back and converting to CSV...")

        people_that_do_not_follow_back = list(filter(lambda u: u not in self.__followers, self.__followees))
        people_that_do_not_follow_back_df = pd.DataFrame(people_that_do_not_follow_back, columns=["Username"])
        people_that_do_not_follow_back_df.to_csv("people_that_do_not_follow_back.csv", index=False)

        return people_that_do_not_follow_back

    def __get_similar_accounts(self) -> list[str]:
        logger.info("Retrieving the usernames of all similar accounts and converting to CSV...")

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
            logger.critical(traceback.format_exc())
        finally:
            instagram_instance.end_session()

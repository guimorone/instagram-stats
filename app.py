import os
import sys
import timeit
import traceback
import pandas as pd
import instaloader
from typing import List, Tuple, Optional, Set, Iterator, Any
from instaloader.nodeiterator import NodeIterator
from instaloader.exceptions import (
    TwoFactorAuthRequiredException,
    ConnectionException,
    BadCredentialsException,
    ProfileNotExistsException,
)
from pick import pick
from utils.misc import setup_logger, get_runtime_text
from utils.constants import MAXIMUM_LOGIN_TRIES

logger = setup_logger(__name__)


class InstaBot:
    def __init__(self, username: str, password: str, *args: Any, **kwargs: Any) -> None:
        self.__username: str = username.strip()
        self.__password: str = password.strip()
        self.__Loader: instaloader.Instaloader = instaloader.Instaloader(*args, **kwargs)
        self.__profile: Optional[instaloader.Profile] = None
        self.profile_to_fetch: str = ""
        self.__followers: Set[str] = set()
        self.__followees: Set[str] = set()
        self.__people_that_do_not_follow_back: Set[str] = set()
        self.__similar_accounts: Set[str] = set()
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
        self.__method_applied: str = ""

    # GETTERS AND SETTERS
    def see_all_methods_as_list(self, upper_names: bool = True) -> List[str]:
        return [m.upper() if upper_names else m for m in self.__all_methods.keys()]

    def see_current_method(self) -> str:
        return self.__method_applied

    def get_followers_list(self) -> Set[str]:
        return self.__followers

    def get_followees_list(self) -> Set[str]:
        return self.__followees

    def get_people_that_do_not_follow_back_list(self) -> Set[str]:
        return self.__people_that_do_not_follow_back

    def get_similar_accounts_list(self) -> Set[str]:
        return self.__similar_accounts

    # PUBLIC METHODS
    def run(self, method_choose: str) -> None:
        if not method_choose:
            return

        self.__start_time: float = timeit.default_timer()
        self.__method_applied: str = method_choose
        self.__login()
        login_tries = 1
        while True:
            try:
                self.__all_methods.get(self.__method_applied).get("method")()
            except ConnectionException:
                logger.error(f"Connection expired, logging in again ({login_tries}º attempt)...")
                login_tries += 1
                self.__login()
                if login_tries > MAXIMUM_LOGIN_TRIES:
                    logger.critical("Too many login attempts, exiting...")
                    break
            except:
                traceback.print_exc()
                logger.critical(f"{self.__method_applied} FAILED TO EXECUTE!")
                break
            else:
                break

    def convert_to_csv(self, data: Set[str], file_name: str, columns: List[str] = ["Username"]) -> None:
        df = pd.DataFrame(data, columns=columns)
        if 'data' not in os.listdir():
            os.mkdir('data')
        df.to_csv(f"data/{file_name}.csv", index=False)

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
            while True:
                try:
                    self.__Loader.two_factor_login(code)
                except BadCredentialsException:
                    logger.error("Invalid verification code, try again!")
                    code = input("Verification Code (try again): ")
                else:
                    break

    def __get_followers_stats(self) -> None:
        self.__profile, num_followers, num_followees = self.__get_profile()
        self.__followers = self.__get_list(
            self.__profile.get_followers(), f"followers_{self.__profile.username}", num_followers
        )
        self.__followees = self.__get_list(
            self.__profile.get_followees(), f"followees_{self.__profile.username}", num_followees
        )
        self.__people_that_do_not_follow_back = self.__get_people_that_do_not_follow_back(
            f"people_that_do_not_follow_back_{self.__profile.username}"
        )
        self.__similar_accounts = self.__get_list(
            self.__profile.get_similar_accounts(), f"similar_accounts_{self.__profile.username}"
        )

    def __get_profile(self) -> Tuple[instaloader.Profile, int, int]:
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

        return profile, num_followers, num_followees

    def __get_list(
        self,
        iterator: NodeIterator[instaloader.Profile] | Iterator[instaloader.Profile],
        file_name: str,
        num_to_check: Optional[int] | None = None,
        columns: List[str] = ["Username"],
    ) -> Set[str]:
        logger.info(f"Retrieving the usernames of all {file_name} and converting to CSV...")

        data = {profile.username for profile in iterator}
        if num_to_check is not None and len(data) < num_to_check:
            logger.warning(f"Only {len(data)} {file_name} were found, less than {num_to_check}!")
        self.convert_to_csv(data, file_name, columns)

        return data

    def __get_people_that_do_not_follow_back(self, file_name: str) -> Set[str]:
        logger.info("Retrieving the usernames of all people that do not follow back and converting to CSV...")

        people_that_do_not_follow_back = set(filter(lambda u: u not in self.__followers, self.__followees))
        self.convert_to_csv(people_that_do_not_follow_back, file_name)

        return people_that_do_not_follow_back


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.warning(f"Usage: `python {sys.argv[0]} USERNAME PASSWORD`")
        logger.error("Set your credentials properly and try again!")
        sys.exit(1)

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

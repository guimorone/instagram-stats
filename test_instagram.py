import pandas as pd
import sys
import traceback
import timeit
from random import randint
from time import sleep

import instaloader
from instaloader.exceptions import TwoFactorAuthRequiredException, ConnectionException


class MyRateController(instaloader.RateController):
    def count_per_sliding_window(self, query_type):
        return 30

    def wait_before_query(self, query_type):
        # Get random sleep time
        sleep_per_req = randint(5, 15)
        sleep(sleep_per_req)

        return


def main(username: str, password: str, L: instaloader.Instaloader):
    def login(user: str, passwd: str):
        try:
            print("Logging in...")
            L.login(user, passwd)
        except TwoFactorAuthRequiredException:
            code = input("Verification Code: ")
            while not code:
                print("--- Error while trying to send the verification code ---")
                code = input("Try again: ")
            L.two_factor_login(code)

    login(username, password)

    profile_to_fetch = input("Profile to fetch (skip to fetch the logged account): ")
    profile_to_fetch = profile_to_fetch if profile_to_fetch else username
    print(f"Loading {profile_to_fetch} profile from an Instagram handle...")
    profile = instaloader.Profile.from_username(L.context, profile_to_fetch)

    print("Retrieving the usernames of all followers and followings...")
    followers = [follower.username for follower in profile.get_followers()]
    followings = [followee.username for followee in profile.get_followees()]

    print("Retrieving the usernames of all people that do not follow back...")
    people_that_do_not_follow_back = list(
        filter(lambda username: username not in followers, followings)
    )

    print("Converting the data to a DataFrame...")
    followers_df = pd.DataFrame(followers)
    followings_df = pd.DataFrame(followings)
    people_that_do_not_follow_back_df = pd.DataFrame(people_that_do_not_follow_back)

    print("Storing the results in a CSV file...")
    followers_df.to_csv("followers.csv", index=False)
    followings_df.to_csv("followings.csv", index=False)
    people_that_do_not_follow_back_df.to_csv(
        "people_that_do_not_follow_back.csv", index=False
    )

    print("-------------- NUMBERS --------------")
    print("Followers:", len(followers))
    print("Followings:", len(followings))
    print("People that do not follow back:", len(people_that_do_not_follow_back))
    print("-------------------------------------")


if __name__ == "__main__":
    start = timeit.default_timer()

    if len(sys.argv) != 3:
        print("Set your credentials properly and try again")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        L = instaloader.Instaloader(rate_controller=lambda ctx: MyRateController(ctx))
        try:
            main(username, password, L)
        except:
            traceback.print_exc()
        finally:
            L.close()

    stop = timeit.default_timer()
    print("Runtime: ", stop - start)

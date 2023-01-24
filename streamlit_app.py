import streamlit as st
import time
import pandas as pd

import instaloader
from instaloader.exceptions import (
    TwoFactorAuthRequiredException,
    ConnectionException,
    BadCredentialsException,
)

st.set_page_config(
    "Instagram stats",
    "📷",
    menu_items={
        "Get Help": "https://github.com/guimorone/instagram-followers",
        "Report a bug": "https://github.com/guimorone/instagram-followers/issues",
        "About": "Get CSV files of the followers, the followings, and the people that do not follow back the account that you choose.",
    },
)
st.header("Instagram stats")
st.subheader(
    "Get CSV files of the followers, the followings, and the people that do not follow back the account that you choose."
)


class MyRateController(instaloader.RateController):
    pass


@st.cache
def convert_df(df: pd.DataFrame, index: bool = False):
    return df.to_csv(index=index).encode("utf-8")


class InstaBot:
    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password
        self.__Loader = instaloader.Instaloader(
            rate_controller=lambda ctx: MyRateController(ctx)
        )

        self.followers = []
        self.followings = []
        self.people_that_do_not_follow_back = []

    def run(self):
        self.login()
        if "program_status" in st.session_state and not st.session_state.program_status:
            st.stop()
        self.get_profile()

    def login(self):
        try:
            with st.spinner(f"Logging into {self.__username} account..."):
                self.__Loader.login(self.__username, self.__password)
        except TwoFactorAuthRequiredException:
            code = st.number_imput("Verification Code: ")
            while not code:
                st.error("--- Error while trying to send the verification code ---")
                code = st.number_imput("Try again: ")
            with st.spinner(f"Logging into {self.__username} account..."):
                self.__Loader.two_factor_login(code)
        except ConnectionException:
            st.warning("Too many requests of login in this account, try again later!")
        except (ConnectionException, BadCredentialsException) as e:
            st.error("Invalid credentials")
            st.error(e)
            st.session_state.program_status = False

    def get_profile(self):
        col_profile, col_button_profile = st.columns(2, gap="medium")
        with col_profile:
            profile_to_fetch = st.text_input(
                "Profile",
                help="Skip to fetch the logged account",
                value=self.__username,
                placeholder="Profile",
            )
        with col_button_profile:
            if st.button(
                "Fetch profile",
                help=f"Fetch {profile_to_fetch} account",
                type="primary",
                disabled=not profile_to_fetch,
            ):
                if not profile_to_fetch:
                    profile_to_fetch = self.__username
                with st.spinner(
                    f"Loading {profile_to_fetch} profile from an Instagram handle..."
                ):
                    profile = instaloader.Profile.from_username(
                        self.__Loader.context, profile_to_fetch
                    )

                self.followers = self.get_followers(profile)
                self.followings = self.get_followees(profile)
                self.people_that_do_not_follow_back = (
                    self.get_people_that_do_not_follow_back()
                )

                self.__Loader.close()

    def get_followers(self, profile: instaloader.Profile):
        with st.spinner(
            "Retrieving the usernames of all followers and converting to CSV..."
        ):
            followers = [follower.username for follower in profile.get_followers()]
            self.followers_df = pd.DataFrame(followers, columns=["Username"])

        return followers

    def get_followees(self, profile: instaloader.Profile):
        with st.spinner(
            "Retrieving the usernames of all followings and converting to CSV..."
        ):

            followings = [followee.username for followee in profile.get_followees()]
            self.followings_df = pd.DataFrame(followings, columns=["Username"])

        return followings

    def get_people_that_do_not_follow_back(self):
        with st.spinner(
            "Retrieving the usernames of all people that do not follow back and converting to CSV..."
        ):
            people_that_do_not_follow_back = list(
                filter(lambda u: u not in self.followers, self.followings)
            )
            self.people_that_do_not_follow_back_df = pd.DataFrame(
                people_that_do_not_follow_back, columns=["Username"]
            )

        return people_that_do_not_follow_back

    def debug_numbers(self):
        col3, col4, col5 = st.columns(3)
        with col3:
            st.dataframe(self.followers_df)
            csv = convert_df(self.followers_df)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="followers.csv",
                mime="text/csv",
            )
        with col4:
            st.dataframe(self.followings_df)
            csv = convert_df(self.followings_df)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="followings.csv",
                mime="text/csv",
            )
        with col5:
            st.dataframe(self.people_that_do_not_follow_back_df)
            csv = convert_df(self.people_that_do_not_follow_back_df)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="people_that_do_not_follow_back.csv",
                mime="text/csv",
            )

        with st.sidebar:
            st.info("------ NUMBERS ------")
            st.success(f"Followers: {len(self.followers)}")
            st.success(f"Followings: {len(self.followings)}")
            st.success(
                f"People that do not follow back: {len(self.people_that_do_not_follow_back)}"
            )


def main():
    was_clicked = False
    with st.form("initial_credentials"):
        if "program_status" not in st.session_state:
            st.session_state.program_status = True
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
        was_clicked = st.form_submit_button("Run")

    if was_clicked:
        if username and password:
            start_time = time.time()
            with st.sidebar:
                st.write("Progress")
            try:
                bot = InstaBot(username, password)
                bot.run()
            except Exception as err:
                st.error("Error while trying to run the program. Try again later!")
                st.exception(err)
                st.session_state.program_status = False
            with st.sidebar:
                end_time = time.time()
                full_time = end_time - start_time
                minutes = full_time // 60
                seconds = int(full_time - (minutes * 60))
                if minutes:
                    st.markdown(
                        f"### Runtime: {minutes} {'minutes' if minutes > 1 else 'minute'} e {seconds} {'seconds' if seconds > 1 else 'second'} "
                    )
                else:
                    st.markdown(
                        f"### Runtime: {seconds} {'seconds' if seconds > 1 else 'second'}"
                    )
            if st.session_state.program_status:
                st.balloons()
            else:
                st.stop()
        else:
            st.error("Set your credentials properly and try again!")
            st.stop()


main()

# Description

Execute instagram commands:

- **GET_FOLLOWERS_STATS**: Get CSV files of the followers, the followings, and the people that do not follow back the account that you choose.

## Requirements

- Python 3.13.2

Libs at `requirements.txt`

## Usage

```sh
  pip install -r requirements.txt
```

As the normal login was not working properly, the usage of the instaloader `load_session` method was used. This method requires a session object to be created first:

```python
# Login to Instagram with your username and password on your Browser
# Then, open the developer tools (F12) and go to the Application tab
# Look for the Cookies section and find the cookies for Instagram
# Copy the values for the following cookies:
# csrftoken, ds_user_id, ig_did, mid, sessionid
session_context = {
    "csrftoken": "Token",
    "ds_user_id": "Token",
    "ig_did": "Token",
    "mid": "Token",
    "sessionid": "Token"
}
```

Paste the values in the `session_context` dictionary in the `app.py` file.

Then, run the script with the following command:

```sh
  python app.py {USERNAME}
```

Where `{USERNAME}` is the username you have used to get the cookies.

## Notes

- If the account has two-factor authentication, it will be requested on the terminal.
- The search profile and the logged account may or may not be the same, it is not mandatory depending on the method to use.
- It is recommended to use a test account to login.
- If you're having trouble logging into the account, try logging in to the browser first or confirm the login activity in the app.
- Instagram API limits the number of requests, so it is recommended to use it with caution, as it may block the account (not forever normally).
- The CSV files will be saved in the `data` folder.

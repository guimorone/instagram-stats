# Description

Get CSV files of the followers, the followings, and the people that do not follow back the account that you choose.

# Local

## Requirements

- Python 3.11.0

Libs at `requirements.txt`

## Usage

USERNAME = username of the account to log in
PASSWORD = password of the account to log in

```sh
  python test_instagram.py USERNAME PASSWORD
```

After that:

- If the account has two-factor authentication, it will be requested in the terminal.
- Choose the profile to fetch in the terminal.

# Streamlit

libs at `requirements-streamlit.txt`

# Notes

- The search profile and the logged account may or may not be the same, it is not mandatory.
- If you're having trouble logging into the account, try logging in to the browser first.

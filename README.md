# Description

Execute instagram commands:

- **GET_FOLLOWERS_STATS**: Get CSV files of the followers, the followings, and the people that do not follow back the account that you choose.

## Requirements

- Python 3.12.3
- Poetry 1.8.3

Libs at `pyproject.toml`

## Usage

```sh
  pip install poetry=='1.8.3'
  poetry install
```

USERNAME = username of the account to log in

PASSWORD = password of the account to log in

```sh
  python app.py {USERNAME} {PASSWORD}
```

## Notes

- If the account has two-factor authentication, it will be requested on the terminal.
- The search profile and the logged account may or may not be the same, it is not mandatory depending on the method to use.
- If you're having trouble logging into the account, try logging in to the browser first or confirm the login activity in the app.
- If you want to try a faster way, set `add_before_query_secs` to `False`. But, pay attention, it may cause fails in the requests.

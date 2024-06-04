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
- It is recommended to use a test account to login.
- If you're having trouble logging into the account, try logging in to the browser first or confirm the login activity in the app.
- Instagram API limits the number of requests, so it is recommended to use it with caution, as it may block the account (not forever normally).
- The CSV files will be saved in the `data` folder.
- The CSV files will be saved with the name of the account that you choose.
- The CSV files will be saved with the following format: `followers_{USERNAME}.csv`, `followings_{USERNAME}.csv`, `not_follow_back_{USERNAME}.csv`.

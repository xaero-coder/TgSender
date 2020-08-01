# Telegram Sender

> Send message or file to user or list of user in telegram and get file from telegram without any requirements

---

## Initialization

> First time to create config.json file run command:

```shell
$ python3 tg_sender.py init
```

- Example config file

```python
{
  "USERS_DICT": {
    "Vahid": 12345678, # Telegram Id
    "Hhz": 12345679,
    "Admin": ["Vahid", "Hhz"] # list of users name
  },
  "BOT_TOKEN": "jdaflkjlrkjwerjewklmdf3243j32"
}
```

---

## SEND Message

```shell
$ python3 tg_sender.py msg "Hello" "Vahid, Hhz"
$ python3 tg_sender.py msg "Hello" "Admin"
```

--- 

## SEND File

```shell
$ python3 tg_sender.py file "/path/to/file" "Admin"
```
--- 

## GET File

> Get the latest file sent to the bot

```shell
$ python3 tg_sender.py pull
```

---

- If there was a problem in the files, notify me!

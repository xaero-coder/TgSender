# Telegram Sender

> Send message or file to user or list of user in telegram and get file from telegram without any requirements

---

## Example (config.json file)

> First time to create config.json file run command:

```shell
$ python3 tg_sender.py init
```

```python
{
  "USERS_DICT": {
    "Vahid": 12345678, // Telegram Id
    "Hhz": 12345679,
    "Admin": ["Vahid", "Hhz"] // list of users name
  }
  
  "BOT_TOKEN": "jdaflkjlrkjwerjewklmdf3243j32"
}
```

---

## Example (send message)

```shell
$ python3 tg_sender.py msg "Hello" "Vahid, Hhz"
$ python3 tg_sender.py msg "Hello" "Admin"
```

--- 

## Example (send file)

```shell
$ python3 tg_sender.py file "/path/to/file" "Admin"
```
--- 

## Example (get file)

> Get the latest file sent to the bot

```shell
$ python3 tg_sender.py pull
```

---

- If there was a problem in the files, notify me!

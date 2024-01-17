# HollowLink.xyz


## Set up

This site was developed against Python 3.10.12, so you should first have that version of Python installed. Other versions (3.11) probably work too.

### Linux Environment

```
sudo apt update
sudo apt install redis-server
sudo nano /etc/redis/redis.conf # set line `supervised no` to `supervised systemd`
sudo systemctl restart redis
sudo systemctl status redis
```

### App Configurations

- Create a long, random string (`import secrets` `secrets.token_urlsafe(64)`) in a file called `secret.txt`.
- Copy the file called `rename_to_configs.py` and rename it to `configs.py`, then configure all the variables in `configs.py`.
- A new database will be created for you automatically, but if you want to create one manually, run `init_database.py`. You can also drop-in an existing database.
- Flush redis records `redis-cli flushall`.

### App Environment

```
git clone https://github.com/skwzrd/hollowlink.git
mv hollowlink hollowlink
cd hollowlink

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

python3 main.py
```

### Formatting

- `djhtml ./templates`
- `isort ./`
- `black --line-length=140 --target-version=py310 .`


### Linting

- `pylint -d C <module_name>`


## Hosting on Ubuntu

`sudo nano /etc/systemd/system/hollowlink.service`

```service
[Unit]
Description=HollowLink - Gunicorn Service
After=network.target

[Service]
User=user1
Group=www-data

WorkingDirectory=/home/user1/hollowlink
Environment="PATH=/home/user1/hollowlink/venv/bin"
ExecStart=/home/user1/hollowlink/venv/bin/gunicorn -w 2 -b 127.0.0.1:8080 'main:app'

Type=simple
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

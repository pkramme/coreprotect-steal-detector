# coreprotect-steal-detector

This tool detects when items are stolen from chests inside a specific location. Specific locations are defined by a base database, such as this:
```
[examplebase]
x1 = 320
x2 = 380
z1 = 40
z2 = 150
allowedplayers = someplayer,anotherone,onemore
```

Another configuration file is needed to start the application:
```
[webhook]
url = https://path/to/a/webhook/endpoint
user = http-basic-auth-user-here
password = and-the-password-here

[paths]
db = path/to/coreprotect
basedb = path/to/base/database
```
Pull the dependencies with `pipenv install`
Finally you can start the application `pipenv run python3 main.py --config path-to-config`.

I am using this with [n8n](https://github.com/n8n-io/n8n) to send steal events to a discord server.

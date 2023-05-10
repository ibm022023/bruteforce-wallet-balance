# bruteforce-wallet-balance
Scripts with the functionality of create 12 words seed, create BTC wallet and check online if the balance is positive, in case save the address and the private key.
It can check around 190 wallet every second (300 on AWS istance), around 16'416'000 every day, but it depends on your hardware.

## A lot of API key
It's also a collection of BTC API that i found on internet

## Setup
Run ```pip install name_module``` to install missing modules

## Start
```python3 multithreading_multiple_address.py```

## Run on aarch64
Run it on low istance on AWS or raspberry pi 4b can not work, sometimes it throw this error ***ValueError: unsupported hash type ripemd160***

[Solution source](https://stackoverflow.com/questions/72409563/unsupported-hash-type-ripemd160-with-hashlib-in-python/72508879#72508879)

To avoid this and run without problems, follow this steps:
Find where is your openssl directory: ```openssl version -d```

You can now go to the directory and edit the config file with sudo: ```nano openssl.cnf```

Make sure that the config file contains following lines:
```
openssl_conf = openssl_init

[openssl_init]
providers = provider_sect

[provider_sect]
default = default_sect
legacy = legacy_sect

[default_sect]
activate = 1

[legacy_sect]
activate = 1
```


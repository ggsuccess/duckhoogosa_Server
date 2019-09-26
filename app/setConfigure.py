import os
import sys
import json


def set_secret(__name__):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secrets_path = os.path.join(base_dir + '/app/secret.json')
    secrets = json.loads(open(secrets_path).read())
    for key, value in secrets.items():
        setattr(sys.modules[__name__], key, value)

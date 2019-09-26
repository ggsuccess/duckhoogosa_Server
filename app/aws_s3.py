import sys
import os

import boto3
from botocore.exceptions import NoCredentialsError

from requests import get  # to make GET request
import ssl
import pprint

from setConfigure import set_secret

set_secret(__name__)
ssl._create_default_https_context = ssl._create_unverified_context
AWS_ACCESS_KEY = getattr(sys.modules[__name__], 'AWS_ACCESS_KEY')
AWS_AUTH_ACCESS_KEY = getattr(sys.modules[__name__], 'AWS_AUTH_ACCESS_KEY')

print("AWS connection init")

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_AUTH_ACCESS_KEY)


def upload_file(local_file_path, target_key_name):
    print(local_file_path, target_key_name, "좀!")
    try:
        s3.upload_file(local_file_path, 'duckhoogosa', target_key_name)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def download(url, file_name):
    with open(os.getcwd() + "/download/" + file_name, "wb") as file:  # open in binary mode
        response = get(url)  # get request
        file.write(response.content)  # write to file

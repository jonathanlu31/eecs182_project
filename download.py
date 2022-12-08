import pandas as pd
import os
import hashlib
import hmac
import base64
import urllib.parse as urlparse
import shutil


import requests


data_path = os.path.join('./', 'GPS_hhds.dta') # cannot share this file as the GPS location are confidential according to the professor


df = pd.read_stata(data_path)


def sign_url(input_url=None, secret=None):
    """ Sign a request URL with a URL signing secret.
      Usage:
      from urlsigner import sign_url
      signed_url = sign_url(input_url=my_url, secret=SECRET)
      Args:
      input_url - The URL to sign
      secret    - Your URL signing secret
      Returns:
      The signed request URL
  """

    if not input_url or not secret:
        raise Exception("Both input_url and secret are required")

    url = urlparse.urlparse(input_url)

    # We only need to sign the path+query part of the string
    url_to_sign = url.path + "?" + url.query

    # Decode the private key into its binary format
    # We need to decode the URL-encoded private key
    decoded_key = base64.urlsafe_b64decode(secret)

    # Create a signature using the private key and the URL-encoded
    # string using HMAC SHA1. This signature will be binary.
    signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)

    # Encode the binary signature into base64 for use within a URL
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

    # Return signed URL
    return original_url + "&signature=" + encoded_signature.decode()

  



def construct_url(loc_data, zoom=19):
    BASE_URL = "https://maps.googleapis.com/maps/api/staticmap?center={}%2C{}&zoom={}&scale={}&size={}&maptype={}&format=png&key={}"
    lat = loc_data['a_latitude']
    long = loc_data['a_longitude']
    scale = 2
    size = "300x300"
    maptype= 'satellite'
    key = input('input API Key')
    return BASE_URL.format(lat, long, zoom, scale, size, maptype, key)
  

secret = input('input signature') 


rand_start = 0 # random.randint(0, len(df)//2)
for i in range(len(df)//2, len(df)):
    image_url = construct_url(df.iloc[i])
    image_url = sign_url(image_url, secret)

    response = requests.get(image_url, stream=True)
    zoom = 19
    if int(response.headers.get('Content-Length')) <= 20000:
        # bad image
        continue
    if (i % 100 == 0):
        print(i)

    with open('./images/image{}-zoom{}.png'.format(i, zoom), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    
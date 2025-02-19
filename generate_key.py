import hmac
import hashlib
import os

secret_key = bytes(os.getenv("ACTIONHUB_SECRET"), "utf-8")
random_key = os.urandom(32).hex()

hmac_object = hmac.new(secret_key, random_key.encode(), hashlib.sha512).hexdigest()


print("Generated authorization key:")
print(secret_key + "/" + hmac_object)
print("Copy this key into Looker Action as authorization key.")
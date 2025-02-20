import hmac
import hashlib
import os

secret_key = bytes("a79a0a190a0d79b39a34ef8ce55d1e742e29729dce7cbcb2845c975f062c6fb7", "utf-8")
random_key = os.urandom(32).hex()

hmac_object = hmac.new(secret_key, random_key.encode(), hashlib.sha512).hexdigest()


print("Generated authorization key:")
print("a79a0a190a0d79b39a34ef8ce55d1e742e29729dce7cbcb2845c975f062c6fb7" + "/" + hmac_object)
print("Copy this key into Looker Action as authorization key.")
import hashlib
from decouple import config
import requests


def ksort(d):
    return [(k, d[k]) for k in sorted(d.keys())]


def checkKey(post_body, key):
    if key in post_body.keys():
        return True
    else:
        return False


def hash_validate_ipn(post_body):
    if checkKey(post_body, "verify_key") & checkKey(post_body, "verify_sign"):
        verifyKeys = post_body["verify_key"].split(",")
        new_params = {}

        for key in verifyKeys:
            new_params[key] = post_body[key]

        storePass = str(config("WEBHOOK_SECRET")).encode()

        hashingStorePass = hashlib.md5(storePass).hexdigest()

        new_params["store_passwd"] = hashingStorePass

        new_params = ksort(new_params)
        hashString = ""
        for key in new_params:
            hashString += key[0] + "=" + str(key[1]) + "&"

        hash_string = hashString.strip("&")
        hash_string_md5 = hashlib.md5(hash_string.encode()).hexdigest()
        if hash_string_md5 == post_body["verify_sign"]:
            return True
        else:
            return False
    else:
        return False


def validate_with_sslcommerz(val_id: str) -> dict:

    response = requests.get(
        config("SSLCOMMERZ_VALIDATION_URL"),
        params={
            "val_id": val_id,
            "store_id": config("SSLCOMMERZ_STORE_ID"),
            "store_passwd": config("WEBHOOK_SECRET"),
            "format": "json",
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()

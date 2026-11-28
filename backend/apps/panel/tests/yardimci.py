import time

from django_otp.oath import TOTP


def guncel_kod(cihaz) -> str:
    t = TOTP(cihaz.bin_key, cihaz.step, cihaz.t0, cihaz.digits, cihaz.drift)
    t.time = time.time()
    return f"{t.token():0{cihaz.digits}d}"

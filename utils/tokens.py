import hmac
import hashlib
import time
import struct
import base64
class OTPGenerator:
    """A class to generate one-time passwords (OTP) using TOTP algorithm."""
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def generate_otp(self):
        """Generate a 6-digit one-time password (OTP) using TOTP algorithm."""
        try:
            secret_key_bytes = base64.b32decode(self.secret_key, casefold=True)
            timestamp = int(time.time()) // 30  # Timestep is 30 seconds
            msg = struct.pack(">Q", timestamp)
            hmac_digest = hmac.new(secret_key_bytes, msg, hashlib.sha1).digest()
            offset = hmac_digest[-1] & 0x0F
            truncated_hash = hmac_digest[offset:offset+4]
            otp_value = struct.unpack(">I", truncated_hash)[0]
            otp_value &= 0x7FFFFFFF  # Mask most significant bit to make it 31 bits
            otp = otp_value % 1000000  # Generate 6-digit OTP
            return str(otp)
        except (TypeError, ValueError, base64.binascii.Error, struct.error):
            # Handle decoding errors or invalid input
            return None

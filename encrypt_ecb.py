from gmssl.sm4 import CryptSM4, SM4_ENCRYPT
import base64

key = b'tiekeyuankp12306'
iv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
crypt_sm4 = CryptSM4()
crypt_sm4.set_key(key, SM4_ENCRYPT)


def encrypt_passwd(password):
    encrypted_passwd = crypt_sm4.crypt_ecb(password.strip().encode())
    encrypted_passwd = base64.b64encode(encrypted_passwd).decode()
    return "@" + encrypted_passwd

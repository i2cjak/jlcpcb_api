from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import string
import time
from dataclasses import dataclass
from typing import Self
from urllib.parse import urlsplit

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


_NONCE_ALPHABET = string.ascii_letters + string.digits
_ENCRYPTED_PREFIX = "{encrypted}"


def _wrap_pem(key_material: str, header: str, footer: str) -> bytes:
    stripped = "".join(line.strip() for line in key_material.strip().splitlines() if line.strip())
    if "BEGIN" in stripped:
        return key_material.encode("utf-8")
    chunks = [stripped[index : index + 64] for index in range(0, len(stripped), 64)]
    pem = "\n".join([header, *chunks, footer, ""])
    return pem.encode("utf-8")


@dataclass(slots=True, kw_only=True)
class JLCAuth:
    app_id: str
    access_key: str
    secret_key: str
    endpoint: str = "https://open.jlcpcb.com"
    context_path: str | None = None
    rsa_public_key: str | None = None
    rsa_private_key: str | None = None

    @classmethod
    def from_env(cls, prefix: str = "JLCPCB_") -> Self:
        return cls(
            app_id=os.environ[f"{prefix}APP_ID"],
            access_key=os.environ[f"{prefix}ACCESS_KEY"],
            secret_key=os.environ[f"{prefix}SECRET_KEY"],
            endpoint=os.environ.get(f"{prefix}ENDPOINT", "https://open.jlcpcb.com"),
            context_path=os.environ.get(f"{prefix}CONTEXT_PATH"),
            rsa_public_key=os.environ.get(f"{prefix}RSA_PUBLIC_KEY"),
            rsa_private_key=os.environ.get(f"{prefix}RSA_PRIVATE_KEY"),
        )

    @staticmethod
    def generate_nonce(length: int = 32) -> str:
        return "".join(secrets.choice(_NONCE_ALPHABET) for _ in range(length))

    def build_string_to_sign(
        self,
        *,
        method: str,
        url: str,
        body: str,
        nonce: str,
        timestamp: int | str,
    ) -> str:
        split = urlsplit(url)
        canonical_uri = split.path
        if split.query:
            canonical_uri = f"{canonical_uri}?{split.query}"
        if self.context_path and canonical_uri.startswith(self.context_path):
            canonical_uri = canonical_uri.removeprefix(self.context_path)
        return f"{method.upper()}\n{canonical_uri}\n{timestamp}\n{nonce}\n{body}\n"

    def sign_string(self, string_to_sign: str) -> str:
        digest = hmac.new(
            self.secret_key.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.b64encode(digest).decode("ascii")

    def build_authorization_header(
        self,
        *,
        method: str,
        url: str,
        body: str = "",
        nonce: str | None = None,
        timestamp: int | None = None,
    ) -> str:
        nonce_value = nonce or self.generate_nonce()
        timestamp_value = int(time.time()) if timestamp is None else int(timestamp)
        string_to_sign = self.build_string_to_sign(
            method=method,
            url=url,
            body=body or "",
            nonce=nonce_value,
            timestamp=timestamp_value,
        )
        signature = self.sign_string(string_to_sign)
        return (
            'JOP '
            f'appid="{self.app_id}",'
            f'accesskey="{self.access_key}",'
            f'timestamp="{timestamp_value}",'
            f'nonce="{nonce_value}",'
            f'signature="{signature}"'
        )

    def encrypt_privacy(self, plain_text: str, *, scheme: str = "oaep-sha1") -> str:
        if plain_text.strip() == "":
            return plain_text
        if not self.rsa_public_key:
            raise ValueError("rsa_public_key is required for privacy encryption")
        public_key = serialization.load_pem_public_key(
            _wrap_pem(
                self.rsa_public_key,
                "-----BEGIN PUBLIC KEY-----",
                "-----END PUBLIC KEY-----",
            )
        )
        if scheme == "oaep-sha1":
            pad = padding.OAEP(
                mgf=padding.MGF1(hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            )
        elif scheme == "pkcs1v15":
            pad = padding.PKCS1v15()
        else:
            raise ValueError(f"unsupported RSA privacy scheme: {scheme}")
        encrypted = public_key.encrypt(plain_text.encode("utf-8"), pad)
        return _ENCRYPTED_PREFIX + base64.b64encode(encrypted).decode("ascii")

    def decrypt_privacy(self, cipher_text: str, *, scheme: str = "oaep-sha1") -> str:
        if cipher_text.strip() == "":
            return cipher_text
        if not cipher_text.startswith(_ENCRYPTED_PREFIX):
            return cipher_text
        if not self.rsa_private_key:
            raise ValueError("rsa_private_key is required for privacy decryption")
        private_key = serialization.load_pem_private_key(
            _wrap_pem(
                self.rsa_private_key,
                "-----BEGIN PRIVATE KEY-----",
                "-----END PRIVATE KEY-----",
            ),
            password=None,
        )
        if scheme == "oaep-sha1":
            pad = padding.OAEP(
                mgf=padding.MGF1(hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            )
        elif scheme == "pkcs1v15":
            pad = padding.PKCS1v15()
        else:
            raise ValueError(f"unsupported RSA privacy scheme: {scheme}")
        payload = base64.b64decode(cipher_text.removeprefix(_ENCRYPTED_PREFIX))
        decrypted = private_key.decrypt(payload, pad)
        return decrypted.decode("utf-8")

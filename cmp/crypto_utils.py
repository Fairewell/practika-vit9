from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
dotenv_path = os.path.join(os.getcwd(), ".env")
print(f".env path: {dotenv_path}")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
if SECRET_KEY is None:
    raise ValueError("Переменная окружения 'TELEGRAM_BOT_API_KEY' не найдена.")
SECRET_KEY = SECRET_KEY.encode()  # Кодируем ключ


# Убедитесь, что ключ имеет длину 16, 24 или 32 байта
def get_aes_key(secret_key: bytes) -> bytes:
    """Генерирует ключ AES на основе секретного ключа."""
    return SHA256.new(secret_key).digest()


def encrypt_string(input_string: str) -> str:
    """Шифрует входную строку с использованием AES."""
    cipher = AES.new(get_aes_key(SECRET_KEY), AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(input_string.encode(), AES.block_size))
    return cipher.iv.hex() + ct_bytes.hex()  # Возвращаем IV и зашифрованные данные


def decrypt_string(encrypted_string: str) -> str:
    """Дешифрует зашифрованную строку."""
    iv = bytes.fromhex(encrypted_string[:32])  # Первые 32 символа - это IV
    ct = bytes.fromhex(
        encrypted_string[32:]
    )  # Остальные символы - зашифрованные данные
    cipher = AES.new(get_aes_key(SECRET_KEY), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()


def hash_string(input_string: str) -> str:
    """Хэширует входную строку с использованием SHA-256."""
    return SHA256.new(input_string.encode()).hexdigest()


b_enc = "maria_user_09072024_buh"
a_enc = encrypt_string(b_enc)
a_hash = hash_string(a_enc)
print(
    f"BEFORE ENC: {b_enc}, \nAFTER: {a_enc}, \nHASH: {a_enc}, \nDECRYPTED(NOHASH): {decrypt_string(a_enc)}"
)

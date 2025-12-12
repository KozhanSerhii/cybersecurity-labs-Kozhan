import base64
import getpass
import sys
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class MessageEncryptor:
    """
    Клас для обробки шифрування та дешифрування повідомлень
    з використанням симетричного алгоритму Fernet (AES).
    """
    
    # Статична сіль для навчальних цілей. 
    # У реальних системах сіль має бути унікальною для кожного користувача.
    STATIC_SALT = b'lab_assignment_static_salt_2025'

    def __init__(self):
        self.backend = default_backend()

    def _derive_key(self, passphrase: str) -> bytes:
        """
        Внутрішній метод генерації криптографічного ключа з пароля.
        Використовує алгоритм PBKDF2HMAC для перетворення рядка в 32-байтний ключ.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.STATIC_SALT,
            iterations=600000, # Збільшено кількість ітерацій для надійності
            backend=self.backend
        )
        # Кодування ключа у формат URL-safe base64, який вимагає Fernet
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    def encrypt(self, plain_text: str, passphrase: str) -> bytes:
        """
        Шифрує текст, використовуючи ключ, згенерований з пароля.
        """
        key = self._derive_key(passphrase)
        cipher_suite = Fernet(key)
        
        encrypted_bytes = cipher_suite.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes

    def decrypt(self, cipher_data: bytes, passphrase: str) -> str:
        """
        Розшифровує дані, використовуючи ключ, згенерований з пароля.
        """
        key = self._derive_key(passphrase)
        cipher_suite = Fernet(key)
        
        try:
            decrypted_bytes = cipher_suite.decrypt(cipher_data)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            return None

def run_application():
    encryptor = MessageEncryptor()

    while True:
        print("\n=== Система безпечного обміну повідомленнями ===")
        print("1. Створити зашифроване повідомлення")
        print("2. Прочитати (розшифрувати) повідомлення")
        print("3. Вихід")
        
        command = input("Введіть номер команди: ").strip()

        if command == '1':
            print("\n--- Генерація шифрограми ---")
            text = input("Введіть текст повідомлення: ")
            if not text:
                print("Помилка: Повідомлення не може бути порожнім.")
                continue
                
            pwd = getpass.getpass("Введіть пароль-ключ: ")
            
            try:
                result = encryptor.encrypt(text, pwd)
                print("\nРезультат шифрування (надішліть це отримувачу):")
                print(f"{result.decode()}")
            except Exception as e:
                print(f"Виникла помилка шифрування: {e}")

        elif command == '2':
            print("\n--- Дешифрування ---")
            cipher_input = input("Вставте отриманий шифр-код: ").strip()
            if not cipher_input:
                print("Помилка: Вхідні дані відсутні.")
                continue
                
            pwd = getpass.getpass("Введіть пароль-ключ для розшифрування: ")

            try:
                # Конвертуємо вхідний рядок у байти
                cipher_bytes = cipher_input.encode('utf-8')
                decrypted_text = encryptor.decrypt(cipher_bytes, pwd)

                if decrypted_text:
                    print("\nУспішно розшифровано:")
                    print(f">>> {decrypted_text}")
                else:
                    print("\nПомилка: Невірний пароль або дані пошкоджено.")
            except Exception:
                print("\nКритична помилка обробки даних.")

        elif command == '3':
            print("Роботу завершено.")
            sys.exit()
        
        else:
            print("Некоректний вибір. Спробуйте ще раз.")

if __name__ == "__main__":
    try:
        run_application()
    except KeyboardInterrupt:
        print("\nПримусове завершення програми.")
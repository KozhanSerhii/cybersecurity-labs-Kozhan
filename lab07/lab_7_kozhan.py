import os
import time
import struct
from datetime import datetime
from typing import Tuple, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Спробуємо імпортувати tabulate для краси, якщо немає - зробимо заглушку
try:
    from tabulate import tabulate
except ImportError:
    def tabulate(data, headers, tablefmt):
        return str(data)

class Analytics:
    """Клас для збору метрик та генерації звіту."""
    def __init__(self):
        self.metrics = []
        self.start_time = time.time()

    def log_step(self, step_name: str, duration: float, size_before: int, size_after: int):
        self.metrics.append({
            "step": step_name,
            "duration": round(duration, 5),
            "size_before": size_before,
            "size_after": size_after,
            "ratio": f"{round((size_after / size_before) * 100, 2)}%" if size_before > 0 else "N/A"
        })

    def print_report(self):
        print("\n" + "="*50)
        print(f"REPORT | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        print(tabulate(self.metrics, headers="keys", tablefmt="grid"))
        
        total_time = sum(m['duration'] for m in self.metrics)
        print(f"\nTotal Pipeline Time: {total_time:.4f} sec")
        print("="*50 + "\n")

class CryptoStegoSystem:
    """
    Комплексна система захисту:
    1. AES Encryption (Fernet)
    2. Steganography (EOF Injection)
    """
    
    # Унікальна сигнатура для розділення картинки та даних
    SEPARATOR = b'<<__SECURE_DATA_START__>>'

    def __init__(self, password: str):
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
        self.analytics = Analytics()

    def _derive_key(self, password: str) -> bytes:
        """Генерація 32-байтного ключа з пароля (PBKDF2)"""
        salt = b'static_salt_for_demo' # У проді генерувати рандомно і зберігати
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def protect(self, input_file: str, container_image: str, output_stego: str):
        """Повний цикл захисту"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File {input_file} not found")

        print(f"[INFO] Starting protection pipeline for: {input_file}")
        
        # --- Етап 1: Шифрування ---
        t_start = time.perf_counter()
        original_size = os.path.getsize(input_file)
        
        with open(input_file, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        t_enc = time.perf_counter() - t_start
        enc_size = len(encrypted_data)
        
        self.analytics.log_step("AES-256 Encryption", t_enc, original_size, enc_size)

        # --- Етап 2: Стеганографія (Injection) ---
        t_start = time.perf_counter()
        container_size = os.path.getsize(container_image)
        
        with open(container_image, 'rb') as f:
            img_data = f.read()
            
        # Логіка склейки: [Image Bytes] + [Separator] + [Encrypted Data]
        stego_data = img_data + self.SEPARATOR + encrypted_data
        
        with open(output_stego, 'wb') as f:
            f.write(stego_data)
            
        t_stego = time.perf_counter() - t_start
        final_size = len(stego_data)
        
        self.analytics.log_step("Stego Injection", t_stego, enc_size, final_size)
        print(f"[SUCCESS] Protected file saved as: {output_stego}")

    def recover(self, stego_file: str, output_restored: str):
        """Повний цикл відновлення"""
        print(f"[INFO] Starting recovery from: {stego_file}")
        
        # --- Відновлення (Extraction) ---
        t_start = time.perf_counter()
        stego_size = os.path.getsize(stego_file)
        
        with open(stego_file, 'rb') as f:
            content = f.read()
            
        # Пошук роздільника
        split_index = content.find(self.SEPARATOR)
        if split_index == -1:
            raise ValueError("Steganography signature not found! File might be corrupted or not protected.")
            
        # Витягуємо тільки зашифровану частину
        encrypted_data = content[split_index + len(self.SEPARATOR):]
        
        t_extract = time.perf_counter() - t_start
        self.analytics.log_step("Data Extraction", t_extract, stego_size, len(encrypted_data))
        
        # --- Розшифрування ---
        t_start = time.perf_counter()
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
        except Exception as e:
            print("[ERROR] Decryption failed! Wrong password or corrupted data.")
            return

        with open(output_restored, 'wb') as f:
            f.write(decrypted_data)
            
        t_decrypt = time.perf_counter() - t_start
        self.analytics.log_step("AES Decryption", t_decrypt, len(encrypted_data), len(decrypted_data))
        
        print(f"[SUCCESS] File restored to: {output_restored}")

    def show_report(self):
        self.analytics.print_report()

# --- Клієнтська частина ---
if __name__ == "__main__":
    # Налаштування
    PASSWORD = "SuperSecretPassword123"
    INPUT_DOC = "zvit.docx"       # Файл, який треба захистити
    IMAGE_CONT = "cat.jpg"        # Картинка-контейнер
    RESULT_STEGO = "secret_image.jpg"
    RESTORED_DOC = "zvit_restored.docx"

    # Створюємо тестові файли, якщо їх немає (для демонстрації)
    if not os.path.exists(INPUT_DOC):
        with open(INPUT_DOC, 'w') as f: f.write("TOP SECRET REPORT DATA " * 500)
    if not os.path.exists(IMAGE_CONT):
        # Створюємо пустий "фейковий" jpg (заголовок), якщо немає картинки
        with open(IMAGE_CONT, 'wb') as f: f.write(b'\xFF\xD8\xFF\xE0' + b'\x00' * 1000)

    # Ініціалізація системи
    system = CryptoStegoSystem(PASSWORD)

    try:
        # 1. Процес захисту
        system.protect(INPUT_DOC, IMAGE_CONT, RESULT_STEGO)
        
        # 2. Імітація передачі даних...
        print("... File sent over network ...")
        
        # 3. Процес відновлення
        system.recover(RESULT_STEGO, RESTORED_DOC)
        
        # 4. Перевірка хешів (Verification)
        import hashlib
        def get_hash(path): return hashlib.md5(open(path,'rb').read()).hexdigest()
        
        orig_hash = get_hash(INPUT_DOC)
        rest_hash = get_hash(RESTORED_DOC)
        
        print(f"\nIntegrity Check:")
        print(f"Original MD5: {orig_hash}")
        print(f"Restored MD5: {rest_hash}")
        if orig_hash == rest_hash:
            print("[PASS] Integrity Verified!")
        else:
            print("[FAIL] Files do not match!")

        # 5. Звіт
        system.show_report()

    except Exception as e:
        print(f"\n[CRITICAL ERROR]: {e}")
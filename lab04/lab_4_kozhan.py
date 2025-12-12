import hashlib
from pathlib import Path

MOD = 1_000_007
PUB_MULT = 7  # константа для спрощеної математичної моделі публічного ключа

def sha256_bytes(data: bytes) -> bytes:
    # Генерує SHA-256 хеш у вигляді байтового рядка (32 байти)
    return hashlib.sha256(data).digest()

def sha256_hex(data: bytes) -> str:
    # Повертає хеш у шістнадцятковому (hex) форматі для зручного читання
    return hashlib.sha256(data).hexdigest()

def derive_private_key(lastname: str, birthday: str, secret: str) -> bytes:
    # Генерація приватного ключа через хешування об'єднаних особистих даних
    # Приклад вхідних даних: Прізвище, Дата народження, Секретне слово
    seed = (lastname + birthday + secret).encode("utf-8")
    return sha256_bytes(seed)

def public_key_from_private(private_key_bytes: bytes) -> int:
    # Обчислення публічного ключа за заданим спрощеним алгоритмом:
    # перетворення байтів у число -> (private_key * 7) % 1_000_007
    priv_int = int.from_bytes(private_key_bytes, byteorder="big")
    return (priv_int * PUB_MULT) % MOD

def xor_bytes(a: bytes, b: bytes) -> bytes:
    # Виконання операції XOR між двома послідовностями байтів (імітація шифрування)
    # Якщо ключ коротший за дані, він повторюється циклічно
    kb = (b * (len(a) // len(b) + 1))[:len(a)]
    return bytes(x ^ y for x, y in zip(a, kb))

def sign_file(path: str, private_key_bytes: bytes) -> bytes:
    # Процес підписання: Хеш вмісту файлу XOR Приватний ключ
    content = Path(path).read_bytes()
    h = sha256_bytes(content)
    return xor_bytes(h, private_key_bytes)

def verify_file(path: str, signature: bytes, public_key: int, private_key_bytes: bytes) -> bool:
    # Алгоритм перевірки цифрового підпису:
    # 1) Валідація пари ключів (публічний має відповідати приватному за формулою)
    if public_key_from_private(private_key_bytes) != public_key:
        return False  # помилка: ключі математично не пов'язані
    
    # 2) Обчислення актуального хешу файлу та дешифрування підпису
    content = Path(path).read_bytes()
    current_hash = sha256_bytes(content)
    recovered_hash = xor_bytes(signature, private_key_bytes)
    
    # 3) Порівняння: якщо хеші ідентичні, підпис вважається вірним
    return recovered_hash == current_hash

def main():
    print("=== Демонстрація роботи ЕЦП (Навчальна версія) ===")

    # Блок введення даних користувача для ініціалізації системи
    lastname = input("Ваше прізвище (напр. Шевченко): ").strip()
    birthday = input("Дата народження (формат ДДММРРРР): ").strip()
    secret = input("Секретне слово-пароль: ").strip()
    doc_path = input("Вкажіть шлях до файлу (напр. document.txt): ").strip()

    # Генерація ключів на основі введених даних
    priv = derive_private_key(lastname, birthday, secret)
    pub = public_key_from_private(priv)

    print(f"\nЗгенеровано ПРИВАТНИЙ ключ (hex): {priv.hex()}")
    print(f"Згенеровано ПУБЛІЧНИЙ ключ (int): {pub}")

    # Головне меню програми
    while True:
        print("\nМеню операцій:")
        print("1) Підписати файл")
        print("2) Перевірити дійсність підпису")
        print("3) Тест на цілісність (симуляція атаки)")
        print("4) Завершити роботу")
        choice = input("Введіть номер опції: ").strip()

        if choice == "1":
            # Створення підпису
            try:
                signature = sign_file(doc_path, priv)
                print(f"Успішно підписано. Ваш підпис (hex): {signature.hex()}")
            except FileNotFoundError:
                print("Увага: Файл відсутній за вказаним шляхом.")
        
        elif choice == "2":
            # Перевірка підпису користувача
            sig_hex = input("Вставте підпис для перевірки (hex): ").strip()
            try:
                signature = bytes.fromhex(sig_hex)
                is_valid = verify_file(doc_path, signature, pub, priv)
                print("Статус перевірки:", "ПІДПИС ВІРНИЙ" if is_valid else "ПІДПИС НЕВАЛІДНИЙ / ПІДРОБКА")
            except ValueError:
                print("Помилка формату даних (очікується hex-рядок).")
            except FileNotFoundError:
                print("Увага: Файл відсутній за вказаним шляхом.")
        
        elif choice == "3":
            # Демонстрація чутливості алгоритму до змін у файлі
            try:
                signature = sign_file(doc_path, priv)          # отримання еталонного підпису
                recovered_hash = xor_bytes(signature, priv)    # відновлення оригінального хешу

                content = Path(doc_path).read_bytes()
                fake_content = content + b"X"                  # вносимо зміни у вміст файлу (атака)
                fake_hash = hashlib.sha256(fake_content).digest()

                print(f"Еталонний підпис (hex): {signature.hex()}")
                print("Результат перевірки зміненого файлу:",
                      "ЗМІНИ ВИЯВЛЕНО (Успіх)" if recovered_hash != fake_hash else "ЗМІНИ ПРОПУЩЕНО (Провал)")
            except FileNotFoundError:
                print("Увага: Файл відсутній за вказаним шляхом.")
        
        elif choice == "4":
            print("Роботу завершено.")
            break
        else:
            print("Невідома команда. Спробуйте варіанти 1-4.")

if __name__ == "__main__":
    main()
def get_ukrainian_alphabet():
    # Український алфавіт + пробіл
    return "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя "

def caesar_cipher(text, shift, decrypt=False):
    alphabet = get_ukrainian_alphabet()
    n = len(alphabet)
    result = ""
    if decrypt: shift = -shift
    for char in text:
        if char in alphabet:
            idx = alphabet.index(char)
            result += alphabet[(idx + shift) % n]
        else:
            result += char
    return result

def vigenere_cipher(text, key, decrypt=False):
    alphabet = get_ukrainian_alphabet()
    n = len(alphabet)
    result = ""
    # Фільтруємо ключ, залишаючи тільки символи з нашого алфавіту
    key_indices = [alphabet.index(k) for k in key if k in alphabet]
    
    if not key_indices: return text
    
    key_len = len(key_indices)
    text_idx = 0
    
    for char in text:
        if char in alphabet:
            char_idx = alphabet.index(char)
            shift = key_indices[text_idx % key_len]
            
            new_idx = (char_idx - shift) % n if decrypt else (char_idx + shift) % n
            result += alphabet[new_idx]
            text_idx += 1
        else:
            result += char
    return result

# --- ОСНОВНА ЧАСТИНА (ІНТЕРАКТИВ) ---

print(f"{'='*60}")
print("   ВВЕДЕННЯ ДАНИХ (Кожан С.В.)")
print(f"{'='*60}")

# 1. Запит даних у користувача
try:
    text_input = input("1. Введіть текст для шифрування: ")
    shift_input = int(input("2. Введіть число зсуву для Цезаря (наприклад, 8): "))
    key_input = input("3. Введіть слово-ключ для Віженера (наприклад, КОЖАН): ")
except ValueError:
    print("\n[ПОМИЛКА] Зсув для Цезаря має бути цілим числом!")
    exit()

# 2. Шифрування
c_enc = caesar_cipher(text_input, shift_input)
v_enc = vigenere_cipher(text_input, key_input)

# 3. Вивід результатів
print(f"\n{'='*60}")
print(f"ПОРІВНЯЛЬНИЙ АНАЛІЗ РЕЗУЛЬТАТІВ")
print(f"{'='*60}\n")

print(f"Вхідний текст: \"{text_input}\"\n")

print(f"1. ШИФР ЦЕЗАРЯ (Ключ = {shift_input})")
print(f"Результат: {c_enc}")
print(f"------------------------------------------------------------")

print(f"2. ШИФР ВІЖЕНЕРА (Ключ = \"{key_input}\")")
print(f"Результат: {v_enc}")
print(f"{'='*60}\n")

# 4. Таблиця порівняння
print(f"{'КРИТЕРІЙ':<20} | {'ШИФР ЦЕЗАРЯ':<25} | {'ШИФР ВІЖЕНЕРА':<25}")
print(f"{'-'*20}-+-{'-'*25}-+-{'-'*25}")
print(f"{'Довжина рез-ту':<20} | {str(len(c_enc)) + ' символів':<25} | {str(len(v_enc)) + ' символів':<25}")
print(f"{'Читабельність':<20} | {'Низька (структурна)':<25} | {'Нульова (хаос)':<25}")
print(f"{'Тип ключа':<20} | {f'Число ({shift_input})':<25} | {f'Слово ({key_input})':<25}")
print(f"\n{'='*60}\n")

# 5. Висновки
print("ВИСНОВКИ ПРО СТІЙКІСТЬ МЕТОДІВ:\n")

print(">> ШИФР ЦЕЗАРЯ:")
print("   Стійкість критично низька. Використання сталого числового зсуву")
print("   дозволяє зловмиснику відновити текст методом простого перебору.")
print("   Зберігаються пробіли та довжина слів.\n")

print(">> ШИФР ВІЖЕНЕРА:")
print(f"   Стійкість значно вища. Використання ключового слова \"{key_input}\"")
print("   робить зсув змінним для кожної літери тексту.")
print("   Це ефективно протидіє частотному аналізу та ускладнює злам.")
print(f"{'='*60}")
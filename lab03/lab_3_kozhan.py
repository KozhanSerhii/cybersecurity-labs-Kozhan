from PIL import Image
import sys
import os

# --- КОНФІГУРАЦІЯ ---
# Маркер (сигнатура), який ми додаємо в кінець нашого тексту.
# Це потрібно, щоб програма знала, де зупинити зчитування, і не читала "шум" решти пікселів.
END_MARKER = bytes([0xFF, 0x00, 0xFF, 0x00]) 

# --- ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ РОБОТИ З БІТАМИ ---

def _to_bits(data_bytes):
    """Генератор, що розбиває байти на окремі біти (0 або 1)."""
    for byte in data_bytes:
        # Проходимо по 8 бітах кожного байта (від 7-го до 0-го)
        for i in range(7, -1, -1):
            # (byte >> i) зсуває біт на позицію одиниць
            # & 1 бере лише останній біт, відкидаючи все інше
            yield (byte >> i) & 1

def _from_bits(bits):
    """Збирає список бітів назад у повноцінні байти (символи)."""
    out = bytearray()
    cur = 0  # Тимчасова змінна для формування байта
    count = 0 
    for b in bits:
        # (cur << 1) зсуває накопичені біти вліво, звільняючи місце
        # | b записує новий біт на вільне місце
        cur = (cur << 1) | b 
        count += 1
        if count == 8: # Коли зібрали 8 біт — маємо готовий байт
            out.append(cur)
            cur = 0
            count = 0
    return bytes(out)

# --- ОСНОВНА ЛОГІКА СТЕГАНОГРАФІЇ ---

def hide_message(cover_path, stego_path, message_text):
    """Вбудовує текст у зображення методом LSB (Least Significant Bit)."""
    
    # 1. Підготовка зображення
    # convert('RGB') гарантує, що у нас 3 канали кольору, без прозорості (Alpha)
    img = Image.open(cover_path).convert('RGB') 
    pixels = img.load() 
    w, h = img.size 

    # 2. Підготовка даних (Payload)
    # Кодуємо текст у байти та додаємо стоп-маркер в кінці
    payload = message_text.encode('utf-8') + END_MARKER 
    bits = list(_to_bits(payload)) 
    
    # Розрахунок ємності: (ширина * висота * 3 кольори) = кількість пікселів для запису
    capacity_bits = w * h * 3 

    if len(bits) > capacity_bits:
        raise ValueError(f"Помилка: Текст завеликий! Потрібно {len(bits)} біт, а доступно {capacity_bits}.")

    # 3. Процес вбудовування
    idx = 0  # Індекс поточного біта, який ми ховаємо
    
    for y in range(h):
        for x in range(w):
            if idx >= len(bits): break # Якщо всі біти записані — виходимо
            
            r, g, b = pixels[x, y] # Отримуємо поточні кольори пікселя

            # --- МАГІЯ LSB ---
            # (val & ~1) -> обнуляє останній біт (наприклад, 1011 -> 1010)
            # | bits[idx] -> записує наш біт секрету (0 або 1) на це місце
            
            if idx < len(bits):
                r = (r & ~1) | bits[idx]
                idx += 1
            
            if idx < len(bits):
                g = (g & ~1) | bits[idx]
                idx += 1
                
            if idx < len(bits):
                b = (b & ~1) | bits[idx]
                idx += 1

            # Оновлюємо піксель новим значенням
            pixels[x, y] = (r, g, b)
        
        if idx >= len(bits): break

    # 4. Збереження результату
    # Важливо: формат PNG, бо JPG стиснення знищить наші приховані біти!
    img.save(stego_path, format='PNG') 
    print(f"[+] Успіх! Дані приховано у файлі: {stego_path}")
    print(f"[i] Статистика: використано {idx} з {capacity_bits} доступних біт.")

def extract_message(stego_path):
    """Витягує приховані дані із зображення."""
    img = Image.open(stego_path).convert('RGB') 
    pixels = img.load()
    w, h = img.size
    bits = []

    # 1. Зчитування всіх молодших бітів
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            # (val & 1) -> повертає лише останній біт числа
            bits.append(r & 1)
            bits.append(g & 1)
            bits.append(b & 1)

    # 2. Реконструкція байтів
    data = _from_bits(bits) 
    
    # 3. Пошук стоп-маркера
    stop_index = data.find(END_MARKER)
    
    if stop_index == -1:
        raise ValueError("Помилка: Маркер кінця повідомлення не знайдено. Можливо, файл пошкоджено або там немає секрету.")
    
    # Декодуємо лише корисну частину (до маркера)
    extracted_text = data[:stop_index].decode('utf-8')
    
    print("\n--- ЗНАЙДЕНО ПОВІДОМЛЕННЯ ---")
    print(extracted_text)
    print("-------------------------------")

# --- ТОЧКА ВХОДУ (ЗАПУСК ПРОГРАМИ) ---
if __name__ == "__main__":
    # Цей блок дозволяє коректно знаходити файли незалежно від того, як запущено VS Code
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Шляхи до файлів (автоматично будуються відносно папки скрипта)
    input_image = os.path.join(script_dir, "test.png")
    output_image = os.path.join(script_dir, "hidden.png")
    
    secret_message = "Сховане повідомлення: Курка чи яйце 12312"

    print(f"[i] Робоча директорія: {script_dir}")

    # Перевірка наявності вхідного файлу
    if not os.path.exists(input_image):
        print(f"[!] КРИТИЧНА ПОМИЛКА: Файл 'test.png' відсутній у папці!")
        print(f"Будь ласка, помістіть будь-яке зображення сюди: {input_image}")
    else:
        try:
            print("\n--- КРОК 1: Приховування даних ---")
            hide_message(input_image, output_image, secret_message)
            
            print("\n--- КРОК 2: Розшифровка даних ---")
            extract_message(output_image)
            
        except Exception as e:
            print(f"[!] Сталася помилка виконання: {e}")
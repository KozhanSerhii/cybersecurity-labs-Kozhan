import sqlite3

def setup_database():
    """Створення БД та наповнення тестовими даними"""
    conn = sqlite3.connect('demo_db.sqlite')
    cursor = conn.cursor()
    
    # Створення таблиці
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        position TEXT,
        salary INTEGER,
        personal_info TEXT
    )
    ''')
    
    # Очищення таблиці перед новим запуском (для чистоти експерименту)
    cursor.execute('DELETE FROM employees')
    
    # Додавання даних
    employees = [
        (1, 'Ivanenko', 'Manager', 15000, 'Passport: AB123456'),
        (2, 'Petrenko', 'Developer', 25000, 'Passport: CD789012'),
        (3, 'Sydorenko', 'Accountant', 18000, 'Passport: EF345678'),
        (4, 'Director', 'CEO', 50000, 'Passport: SECRET_007')
    ]
    
    cursor.executemany('INSERT INTO employees VALUES (?,?,?,?,?)', employees)
    conn.commit()
    conn.close()
    print("[-] База даних успішно створена та наповнена.")

def vulnerable_search(search_term):
    """Вразлива функція пошуку (String Concatenation)"""
    conn = sqlite3.connect('demo_db.sqlite')
    cursor = conn.cursor()
    
    print(f"\n[!] Виконується ВРАЗЛИВИЙ пошук...")
    
    # НЕБЕЗПЕЧНО: Пряма вставка даних у запит
    sql_query = f"SELECT * FROM employees WHERE name = '{search_term}'"
    
    print(f"[DEBUG] Виконуваний SQL-запит: {sql_query}")
    
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        if results:
            for row in results:
                print(f"   Знайдено: {row[1]} | Посада: {row[2]} | Інфо: {row[4]}")
        else:
            print("   Нічого не знайдено.")
    except sqlite3.Error as e:
        print(f"   [SQL Error]: {e}")
        
    conn.close()

def secure_search(search_term):
    """Захищена функція пошуку (Prepared Statements)"""
    conn = sqlite3.connect('demo_db.sqlite')
    cursor = conn.cursor()
    
    print(f"\n[+] Виконується ЗАХИЩЕНИЙ пошук...")
    
    # БЕЗПЕЧНО: Використання знака питання як плейсхолдера
    sql_query = "SELECT * FROM employees WHERE name = ?"
    
    print(f"[DEBUG] Виконуваний SQL-запит: {sql_query} з параметром ('{search_term}')")
    
    try:
        # Параметри передаються окремим аргументом (tuple)
        cursor.execute(sql_query, (search_term,))
        results = cursor.fetchall()
        
        if results:
            for row in results:
                print(f"   Знайдено: {row[1]} | Посада: {row[2]} | Інфо: {row[4]}")
        else:
            print("   Нічого не знайдено.")
    except sqlite3.Error as e:
        print(f"   [SQL Error]: {e}")
        
    conn.close()

def main():
    setup_database()
    
    while True:
        print("\n" + "="*40)
        print("МЕНЮ ДЕМОНСТРАЦІЇ SQL INJECTION")
        print("1. Вразливий пошук")
        print("2. Захищений пошук")
        print("3. Вихід")
        
        choice = input("Обери варіант (1-3): ")
        
        if choice == '3':
            break
            
        search_input = input("Введи прізвище для пошуку: ")
        
        if choice == '1':
            vulnerable_search(search_input)
        elif choice == '2':
            secure_search(search_input)
        else:
            print("Невірний вибір.")

if __name__ == "__main__":
    main()
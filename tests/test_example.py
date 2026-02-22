"""
Exemplo de código com bugs propositais para testar o bot
"""

def get_user_by_id(user_id):
    """Pega usuário do banco - ATENÇÃO: tem SQL injection!"""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ❌ BUG: SQL Injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    return cursor.fetchone()


def find_duplicates(items):
    """Encontra duplicatas - ATENÇÃO: performance ruim!"""
    duplicates = []
    
    # ❌ BUG: O(n²) quando poderia ser O(n)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    
    return duplicates


def process_data(data):
    """Processa dados sem validação"""
    # ❌ BUG: Não valida se data é None
    return data.strip().upper()

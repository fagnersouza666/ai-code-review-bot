# Arquivo com bugs intencionais para testar o bot

def process_user_data(user_id):
    # BUG 1: SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

def calculate_total(items):
    # BUG 2: O(n²) complexity - loop aninhado desnecessário
    total = 0
    for i in range(len(items)):
        for j in range(len(items)):
            if i == j:
                total += items[i]['price']
    return total

def send_email(email_address, message):
    # BUG 3: Missing input validation
    server.send(email_address, message)
    return True

import mysql.connector

# Database configuration
db = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "bank_management"
}

def get_connection():
    return mysql.connector.connect(**db)

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS bank_management")
    cursor.execute("USE bank_management")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            bank_name VARCHAR(50),
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(50),
            balance FLOAT DEFAULT 0
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

class Bank:
    def __init__(self, name):
        self.name = name

    def login(self, username, passwd):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM accounts WHERE bank_name = %s AND username = %s AND password = %s",
            (self.name, username, passwd)
        )
        account = cursor.fetchone()
        cursor.close()
        connection.close()
        if account:
            print(f"Welcome, {username}")
            return True
        print("Invalid username or password")
        return False

    def register(self, username, passwd):
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO accounts (bank_name, username, password, balance) VALUES (%s, %s, %s, %s)",
                (self.name, username, passwd, 0)
            )
            connection.commit()
            print("Account Created Successfully!")
        except mysql.connector.IntegrityError:
            print(f"User {username} already exists!")
        finally:
            cursor.close()
            connection.close()

    def check_balance(self, username):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT balance FROM accounts WHERE bank_name = %s AND username = %s",
            (self.name, username)
        )
        account = cursor.fetchone()
        cursor.close()
        connection.close()
        if account:
            print(f"Total balance of {username}: {account['balance']} rupees")

    def deposit(self, username, amount):
        if amount <= 0:
            print("Amount must be positive")
            return
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE bank_name = %s AND username = %s",
            (amount, self.name, username)
        )
        connection.commit()
        cursor.close()
        connection.close()
        print(f"{amount} rupees deposited successfully!")

    def withdraw(self, username, amount):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT balance FROM accounts WHERE bank_name = %s AND username = %s",
            (self.name, username)
        )
        account = cursor.fetchone()
        if not account or account['balance'] < amount:
            print("Insufficient funds or invalid account.")
        else:
            cursor.execute(
                "UPDATE accounts SET balance = balance - %s WHERE bank_name = %s AND username = %s",
                (amount, self.name, username)
            )
            connection.commit()
            print(f"{amount} rupees withdrawn successfully!")
        cursor.close()
        connection.close()

    def close_account(self, username, passwd):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM accounts WHERE bank_name = %s AND username = %s",
            (self.name, username)
        )
        connection.commit()
        cursor.close()
        connection.close()
        print(f"Account {username} has been closed successfully")

if __name__ == "__main__":
    initialize_database()

    banks = {
        "Bank1": Bank("Bank1"),
        "Bank2": Bank("Bank2"),
        "Bank3": Bank("Bank3"),
        "Bank4": Bank("Bank4")
    }
    while True:
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            bank_name = input("Enter bank name (Bank1/Bank2/Bank3/Bank4): ")
            if bank_name not in banks:
                print("Please enter a valid bank name.")
                continue
            username = input("Enter username: ")
            passwd = input("Enter password: ")

            if banks[bank_name].login(username, passwd):
                while True:
                    print("---Menu---")
                    print("1. Check Balance")
                    print("2. Deposit")
                    print("3. Withdraw")
                    print("4. Close Account")
                    print("5. Logout")
                    choice2 = input("Enter your choice: ")
                    if choice2 == "1":
                        banks[bank_name].check_balance(username)
                    elif choice2 == "2":
                        amount = float(input("Enter the amount: "))
                        banks[bank_name].deposit(username, amount)
                    elif choice2 == "3":
                        amount = float(input("Enter the amount: "))
                        banks[bank_name].withdraw(username, amount)
                    elif choice2 == "4":
                        banks[bank_name].close_account(username, passwd)
                        break
                    elif choice2 == "5":
                        print("Logged Out!")
                        break
                    else:
                        print("Invalid Input! Please enter a valid choice.")
        elif choice == "2":
            bank_name = input("Enter bank name (Bank1/Bank2/Bank3/Bank4): ")
            if bank_name not in banks:
                print("Please enter a valid bank name.")
                continue
            username = input("Enter username: ")
            passwd = input("Enter password: ")
            banks[bank_name].register(username, passwd)
        elif choice == "3":
            print("Exiting! Goodbye!")
            break
        else:
            print("Invalid choice!")

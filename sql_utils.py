import sqlite3
from constants import *
import hashlib
import logging
import uuid
import datetime

class SQLiteUtils():
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.conn = None
        self.cursor = None
        self.create_connection(APP_DATABASE_PATH)
        self.create_payment_methods_table()
        self.create_transactions_table()
        self.create_profiles_table()
        self.create_investment_table()
        self.create_recurring_table()
        self.create_budgeting_tool_table()

    def create_connection(self,db_file):
        """Create a database connection to the SQLite database specified by db_file."""
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file,check_same_thread=False)
            self.logger.info(f"Connected to database: {db_file}")
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")
        
    def close_connection(self,conn):
        """Close the database connection."""
        if conn:
            conn.close()
            self.logger.info("Connection closed.")
    
    def generate_id(self,*args):
        return hashlib.sha256("".join(args).encode()).hexdigest()

    def generate_uuid(self):
        return str(uuid.uuid4())

    def str_to_bool(self,s):
        return str(s).strip().lower() in ['true', '1', 'yes', 'y','True']
    
    def create_transactions_table(self):
        """Create the transactions table if it does not exist."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            vendor TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            bank TEXT NOT NULL,
            mode TEXT NOT NULL,
            cashback INTEGER NOT NULL,
            recurring BOOLEAN NOT NULL,
            frequency TEXT,
            debt BOOLEAN NOT NULL,
            person TEXT,
            kind TEXT NOT NULL,
            bank_id TEXT NOT NULL
            )
            ''')
            self.conn.commit()
            self.logger.info("Transactions table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating transactions table: {e}")

    def insert_transaction(self, transaction):
        """Insert a new transaction into the transactions table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO transactions (
                    id, date, vendor, category, price, bank, mode, cashback, recurring, frequency, debt, person, kind, bank_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction['id'],
                transaction['date'],
                transaction['vendor'],
                transaction['category'],
                transaction['price'],
                transaction['bank'],
                transaction['mode'],
                transaction['cashback'],
                int(transaction['recurring']),
                transaction['frequency'],
                int(transaction['debt']),
                transaction['person'],
                transaction['kind'],
                hashlib.sha256((transaction['bank'] + transaction['mode']).encode()).hexdigest()
            ))
            self.conn.commit()
            self.logger.info("Transaction inserted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting transaction: {e}")

    def fetch_transactions(self, **kwargs):
        """
        Retrieve transactions from the transactions table, optionally filtered by keyword arguments.
        Example: fetch_transactions(vendor="Amazon"), fetch_transactions(kind="-")
        """
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT * FROM transactions'
            params = []
            if kwargs:
                filters = []
                for key, value in kwargs.items():
                    filters.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(filters)
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching transactions: {e}")
            return [{}]

    def update_transaction(self, transaction):
        """Update an existing transaction in the transactions table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                UPDATE transactions SET
                    date = ?,
                    vendor = ?,
                    category = ?,
                    price = ?,
                    bank = ?,
                    mode = ?,
                    cashback = ?,
                    recurring = ?,
                    frequency = ?,
                    debt = ?,
                    person = ?,
                    kind = ?,
                    bank_id = ?
                WHERE id = ?
            ''', (
                transaction['date'],
                transaction['vendor'],
                transaction['category'],
                transaction['price'],
                transaction['bank'],
                transaction['mode'],
                transaction['cashback'],
                int(transaction['recurring']),
                transaction['frequency'],
                int(transaction['debt']),
                transaction['person'],
                transaction['kind'],
                hashlib.sha256((transaction['bank'] + transaction['mode']).encode()).hexdigest(),
                transaction['id']
            ))
            self.conn.commit()
            self.logger.info("Transaction updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating transaction: {e}")

    def delete_transaction(self, transaction_id):
        """Delete a transaction from the transactions table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            self.conn.commit()
            self.logger.info("Transaction deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting transaction: {e}")
    
    def create_payment_methods_table(self):
        """Create the payment methods table if it does not exist."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_methods (
                    id TEXT PRIMARY KEY,
                    bank TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    cashback INTEGER NOT NULL,
                    parent TEXT,
                    acc_number TEXT,
                    due_date TEXT,
                    balance INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            self.logger.info("Payment methods table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating payment methods table: {e}")
    
    def insert_payment_method(self, payment_method):
        """Insert a new payment method into the payment methods table."""
        self.logger.info("Inserting payment method:", payment_method)
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO payment_methods (id, bank, mode, cashback, parent, acc_number, due_date, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.generate_id(payment_method['bank'],payment_method['mode']),
                payment_method['bank'],
                payment_method['mode'],
                payment_method['cashback'],
                payment_method['parent'],
                payment_method.get('acc_number', ''),
                payment_method.get('due_date', ''),
                payment_method['balance']
            ))
            self.conn.commit()
            self.logger.info("Payment method inserted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting payment method: {e}")

    def update_payment_method(self, payment_method_id, **kwargs):
        """
        Update fields of a payment method in the payment_methods table.
        Example: update_payment_method(id, cashback=5, balance=10000)
        """
        if not kwargs:
            self.logger.warning("No fields provided to update.")
            return
        try:
            self.cursor = self.conn.cursor()
            fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(payment_method_id)
            query = f"UPDATE payment_methods SET {fields} WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.logger.info(f"Payment method {payment_method_id} updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating payment method: {e}")

    def get_payment_methods(self):
        """Retrieve all payment methods from the payment methods table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('SELECT * FROM payment_methods')
            rows = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving payment methods: {e}")
            return []
    
    def query_payment_methods(self,**kwargs):
        """Query payment methods based on provided keyword arguments."""
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT * FROM payment_methods WHERE ' + ' AND '.join([f"{key} = ?" for key in kwargs.keys()])
            self.cursor.execute(query, tuple(kwargs.values()))
            rows = self.cursor.fetchall()
            return [dict(zip([column[0] for column in self.cursor.description], row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error querying payment methods: {e}")
            return []
    
    def delete_payment_method_from_table(self, payment_method_id):
        """Delete a payment method from the payment methods table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('DELETE FROM payment_methods WHERE id = ?', (payment_method_id,))
            self.conn.commit()
            self.logger.info("Payment method deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting payment method: {e}")

    def create_categories_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    name TEXT PRIMARY KEY
                )
            ''')
            self.conn.commit()
            self.logger.info("Categories table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating categories table: {e}")

    def fetch_categories(self):
        try:
            self.cursor.execute('SELECT name FROM categories')
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching categories: {e}")
            return []

    def insert_category(self, name):
        try:
            self.cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
            self.conn.commit()
            self.logger.info(f"Category '{name}' inserted successfully.")
        except sqlite3.IntegrityError:
            self.logger.warning(f"Category '{name}' already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting category: {e}")

    def delete_category(self, name):
        try:
            self.cursor.execute('DELETE FROM categories WHERE name = ?', (name,))
            self.conn.commit()
            self.logger.info(f"Category '{name}' deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting category: {e}")

    def create_vendors_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendors (
                    name TEXT PRIMARY KEY,
                    category TEXT NOT NULL
                )
            ''')
            self.conn.commit()
            self.logger.info("Vendors table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating vendors table: {e}")

    def fetch_vendors(self, **kwargs):
        """
        Fetch vendors, optionally filtered by keyword arguments.
        Example: fetch_vendors(name="Amazon"), fetch_vendors(category="Groceries")
        """
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT name, category FROM vendors'
            params = []
            if kwargs:
                filters = []
                for key, value in kwargs.items():
                    filters.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(filters)
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [{"name": row[0], "category": row[1]} for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching vendors: {e}")
            return []

    def insert_vendor(self, name, category):
        try:
            self.cursor.execute('INSERT INTO vendors (name, category) VALUES (?, ?)', (name, category))
            self.conn.commit()
            self.logger.info(f"Vendor '{name}' inserted successfully.")
        except sqlite3.IntegrityError:
            self.logger.warning(f"Vendor '{name}' already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting vendor: {e}")

    def delete_vendor_from_db(self, name):
        try:
            self.cursor.execute('DELETE FROM vendors WHERE name = ?', (name,))
            self.conn.commit()
            self.logger.info(f"Vendor '{name}' deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting vendor: {e}")
    
    def load_start_end_date(self):
        try:
            profile = self.fetch_profile()[0]
            month = datetime.datetime.now().month
            year = datetime.datetime.now().year
            start = datetime.datetime(year, month-1, profile.get("salary_day",1)).date()
            if month == 1:
                start = datetime.datetime(year-1, 12, profile.get("salary_day",1)).date()    
            if month == 12:
                end = datetime.datetime(year + 1, 1, profile.get("salary_day",1)).date()
            else:
                end = datetime.datetime(year, month, profile.get("salary_day",1)).date()
            return (start,end)
        except Exception as e:
            return (datetime.datetime.now().date(), datetime.datetime.now().date())
    
    def fetch_profile(self, **kwargs):
        """
        Fetch profiles, optionally filtered by keyword arguments.
        Example: fetch_profile(name="John")
        """
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT * FROM profile'
            params = []
            if kwargs:
                filters = []
                for key, value in kwargs.items():
                    filters.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(filters)
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching profile: {e}")
            return [{}]
    
    def create_profiles_table(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS profile (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    salary_day INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            self.logger.info("Profile table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating Profile table: {e}")
    
    def insert_profile(self, name, salary_day,user_id):
        """Insert a new profile into the profile table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO profile (user_id ,name, salary_day)
                VALUES (?, ?, ?)
            ''', (user_id, name, salary_day))
            self.conn.commit()
            self.logger.info(f"Profile '{name}' inserted successfully.")
        except sqlite3.IntegrityError:
            self.logger.warning(f"Profile '{name}' already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting profile: {e}")
    
    def update_profile(self, user_id, **kwargs):
        """
        Update fields of a profile in the profile table.
        Example: update_profile("John", salary_day=15)
        """
        if not kwargs:
            self.logger.warning("No fields provided to update.")
            return
        try:
            self.cursor = self.conn.cursor()
            fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(user_id)
            query = f"UPDATE profile SET {fields} WHERE user_id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.logger.info(f"Profile '{user_id}' updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating profile: {e}")
    
    def create_investment_table(self):
        """Create the investment table if it does not exist."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS investment (
                    name TEXT PRIMARY KEY,
                    invested_value INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            self.logger.info("Investment table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating investment table: {e}")

    def insert_investment(self, name, invested_value):
        """Insert a new investment into the investment table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO investment (name, invested_value)
                VALUES (?, ?)
            ''', (name, invested_value))
            self.conn.commit()
            self.logger.info(f"Investment '{name}' inserted successfully.")
        except sqlite3.IntegrityError:
            self.logger.warning(f"Investment '{name}' already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting investment: {e}")

    def update_investment(self, name, **kwargs):
        """
        Update fields of an investment in the investment table.
        Example: update_investment("Stocks", invested_value=5000)
        """
        if not kwargs:
            self.logger.warning("No fields provided to update.")
            return
        try:
            self.cursor = self.conn.cursor()
            fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(name)
            query = f"UPDATE investment SET {fields} WHERE name = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.logger.info(f"Investment '{name}' updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating investment: {e}")

    def delete_investment(self, name):
        """Delete an investment from the investment table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('DELETE FROM investment WHERE name = ?', (name,))
            self.conn.commit()
            self.logger.info(f"Investment '{name}' deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting investment: {e}")

    def fetch_investment(self, **kwargs):
        """
        Fetch investments, optionally filtered by keyword arguments.
        Example: fetch_investment(name="Stocks")
        """
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT * FROM investment'
            params = []
            if kwargs:
                filters = []
                for key, value in kwargs.items():
                    filters.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(filters)
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching investment: {e}")
            return []
        
    def create_recurring_table(self):
        """Create the recurring table if it does not exist."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            vendor TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            bank TEXT NOT NULL,
            mode TEXT NOT NULL,
            cashback INTEGER NOT NULL,
            recurring BOOLEAN NOT NULL,
            frequency TEXT,
            debt BOOLEAN NOT NULL,
            person TEXT,
            kind TEXT NOT NULL,
            bank_id TEXT NOT NULL
            )
            ''')
            self.conn.commit()
            self.logger.info("recurring table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating recurring table: {e}")

    def insert_recurring(self, recurring):
        """Insert a new recurring into the recurring table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO recurring (
                    id, date, vendor, category, price, bank, mode, cashback, recurring, frequency, debt, person, kind, bank_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recurring['id'],
                recurring['date'],
                recurring['vendor'],
                recurring['category'],
                recurring['price'],
                recurring['bank'],
                recurring['mode'],
                recurring['cashback'],
                int(recurring['recurring']),
                recurring['frequency'],
                int(recurring['debt']),
                recurring['person'],
                recurring['kind'],
                hashlib.sha256((recurring['bank'] + recurring['mode']).encode()).hexdigest()
            ))
            self.conn.commit()
            self.logger.info("recurring inserted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting recurring: {e}")

    def fetch_recurring(self, **kwargs):
        """
        Retrieve recurring from the recurring table, optionally filtered by keyword arguments.
        Example: fetch_recurring(vendor="Amazon"), fetch_recurring(kind="-")
        """
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT * FROM recurring'
            params = []
            if kwargs:
                filters = []
                for key, value in kwargs.items():
                    filters.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(filters)
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching recurring: {e}")
            return [{}]

    def update_recurring(self, recurring):
        """Update an existing recurring in the recurring table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                UPDATE recurring SET
                    date = ?,
                    vendor = ?,
                    category = ?,
                    price = ?,
                    bank = ?,
                    mode = ?,
                    cashback = ?,
                    recurring = ?,
                    frequency = ?,
                    debt = ?,
                    person = ?,
                    kind = ?,
                    bank_id = ?
                WHERE id = ?
            ''', (
                recurring['date'],
                recurring['vendor'],
                recurring['category'],
                recurring['price'],
                recurring['bank'],
                recurring['mode'],
                recurring['cashback'],
                int(recurring['recurring']),
                recurring['frequency'],
                int(recurring['debt']),
                recurring['person'],
                recurring['kind'],
                hashlib.sha256((recurring['bank'] + recurring['mode']).encode()).hexdigest(),
                recurring['id']
            ))
            self.conn.commit()
            self.logger.info("recurring updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating recurring: {e}")

    def delete_recurring(self, recurring_id):
        """Delete a recurring from the recurring table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('DELETE FROM recurring WHERE id = ?', (recurring_id,))
            self.conn.commit()
            self.logger.info("recurring deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting recurring: {e}")

    def create_budgeting_tool_table(self):
        """Create the budgeting_tool table if it does not exist."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgeting_tool (
                    category TEXT PRIMARY KEY,
                    spend_limit INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            self.logger.info("Budgeting tool table created successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating budgeting_tool table: {e}")

    def insert_budgeting_tool(self, category, spend_limit):
        """Insert a new category and spend_limit into the budgeting_tool table."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO budgeting_tool (category, spend_limit)
                VALUES (?, ?)
            ''', (category, spend_limit))
            self.conn.commit()
            self.logger.info(f"Budgeting tool entry '{category}' inserted successfully.")
        except sqlite3.IntegrityError:
            self.logger.warning(f"Budgeting tool entry '{category}' already exists.")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting budgeting tool entry: {e}")

    def update_budgeting_tool(self, category, **kwargs):
        """
        Update fields of a budgeting_tool entry.
        Example: update_budgeting_tool("Food", spend_limit=12000)
        """
        if not kwargs:
            self.logger.warning("No fields provided to update.")
            return
        try:
            self.cursor = self.conn.cursor()
            fields = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(category)
            query = f"UPDATE budgeting_tool SET {fields} WHERE category = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.logger.info(f"Budgeting tool entry '{category}' updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating budgeting tool entry: {e}")

    def delete_budgeting_tool(self, category):
        """Delete a budgeting_tool entry by category."""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('DELETE FROM budgeting_tool WHERE category = ?', (category,))
            self.conn.commit()
            self.logger.info(f"Budgeting tool entry '{category}' deleted successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting budgeting tool entry: {e}")

    def fetch_budgeting_tool(self, **kwargs):
        """
        Fetch budgeting_tool entries, optionally filtered by keyword arguments.
        Example: fetch_budgeting_tool(category="Food")
        """
        try:
            self.cursor = self.conn.cursor()
            query = 'SELECT * FROM budgeting_tool'
            params = []
            if kwargs:
                filters = []
                for key, value in kwargs.items():
                    filters.append(f"{key} = ?")
                    params.append(value)
                query += " WHERE " + " AND ".join(filters)
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching budgeting tool entries: {e}")
            return []
    
    def run_query(self, query, params=None, fetch=False):
        """
        Execute any SQL query.
        :param query: SQL query string (with ? placeholders for parameters)
        :param params: Tuple or list of parameters (optional)
        :param fetch: If True, fetch and return results as list of dicts
        :return: List of dicts (if fetch=True and query returns rows), else None
        """
        try:
            self.cursor = self.conn.cursor()
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            if fetch:
                rows = self.cursor.fetchall()
                columns = [column[0] for column in self.cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            else:
                self.conn.commit()
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error running query: {e}")
            return None
import psycopg2

class ClientManager:
    def __init__(self, database, user, password):
        self.conn = psycopg2.connect(database=database, user=user, password=password)
        self.cur = self.conn.cursor()
        self.create_db()
        
            # Функция, создающая структуру БД (таблицы).
    def create_db(self):
        self.cur.execute("""
                        CREATE TABLE IF NOT EXISTS clients(
                        client_id SERIAL PRIMARY KEY,
                        name VARCHAR(40) NOT NULL, 
                        last_name VARCHAR(40) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL
                        );
                        """)

        self.cur.execute("""
                        CREATE TABLE IF NOT EXISTS phone_numbers(
                        phone_number_id SERIAL PRIMARY KEY,
                        phone_number VARCHAR(40),
                        client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE
                        );
                        """)
        self.conn.commit()

    # Функция, позволяющая добавить нового клиента.
    # RETURNING позволяет вернуть данные(в данном случае ID, чтобы в дальнейшем использовать его для сопоставления номера телефона в другой таблице)
    def add_client(self, name, last_name, email, phone_number=None):
        self.cur.execute("""
                INSERT INTO clients(name, last_name, email)
                VALUES(%s, %s, %s) RETURNING client_id; 
                """, (name, last_name, email))
        
        # Получаем ID нового клиента
        client_id = self.cur.fetchone()[0]
        
        if phone_number:
            self.cur.execute("""
                    INSERT INTO phone_numbers(client_id, phone_number)
                    VALUES(%s, %s);
                    """,  (client_id, phone_number))
        self.conn.commit()
        
    # Функция, позволяющая добавить телефон для существующего клиента.
    def add_phone_number(self, client_id, phone_number):
        self.cur.execute("""
                    INSERT INTO phone_numbers(client_id, phone_number)
                    VALUES(%s, %s);
                    """, (client_id, phone_number))
        self.conn.commit()
        
    # Функция, позволяющая изменить данные о клиенте.
    def update_info(self, client_id, name=None,  last_name=None, email=None):
        if name:
            self.cur.execute("""
                        UPDATE clients SET name=%s WHERE client_id=%s;
                        """, (name, client_id))
        if last_name:
            self.cur.execute("""
                        UPDATE clients SET last_name=%s WHERE client_id=%s;
                        """, (last_name, client_id))
        if email:
            self.cur.execute("""
                        UPDATE clients SET email=%s WHERE client_id=%s;
                        """, (email, client_id))
        self.conn.commit()
        
    # Функция, позволяющая удалить телефон для существующего клиента.
    def delete_phone_number(self, phone_number):
        self.cur.execute("""
                    DELETE FROM phone_numbers WHERE phone_number=%s;
                    """, (phone_number,))
        self.conn.commit()
        
    # Функция, позволяющая удалить существующего клиента.
    def delete_client(self, client_id):
        self.cur.execute("""
                    DELETE FROM phone_numbers WHERE client_id=%s;
                    """, (client_id,))
        self.cur.execute("""
                    DELETE FROM clients WHERE client_id=%s;
                    """, (client_id,))
        self.conn.commit()
        
    # Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
    def find_client(self, name=None, last_name=None, email=None, phone_number=None):
        if phone_number:
            self.cur.execute("""
                    SELECT c.client_id 
                    FROM clients c
                    JOIN phone_numbers p ON c.client_id = p.client_id
                    WHERE p.phone_number = %s;
                    """, (phone_number,))
        else:
            self.cur.execute("""
                    SELECT client_id
                    FROM clients
                    WHERE (%s IS NULL OR name = %s)
                    AND (%s IS NULL OR last_name = %s)
                    AND (%s IS NULL OR email = %s);
                    """, (name, name, last_name, last_name, email, email))
            
        result = self.cur.fetchone()
        return result[0] if result else None
    
    def close_connection(self):
        self.cur.close()
        self.conn.close()
                    

manager = ClientManager(database='netology', user='postgres', password='my password')

manager.add_client("Rin", "Hirst", "qwerty@gmail.com", "7894743")
manager.add_phone_number(9,'932737237')
manager.update_info('6', name='Tom')
manager.delete_phone_number('932737237')
manager.delete_client(9)
client = manager.find_client('Olya')
print(client)


        

        

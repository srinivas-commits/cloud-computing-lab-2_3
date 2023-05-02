import sqlite3

# connect to the database file
conn = sqlite3.connect('./instance/products.db')

# create a cursor
c = conn.cursor()

# execute the INSERT statement to add a record to the table
c.execute("INSERT INTO user(name, email, password, is_admin) VALUES ('admin', 'admin@gmail.com', 'admin', True)")

# commit the changes to the database
conn.commit()

# close the database connection
conn.close()
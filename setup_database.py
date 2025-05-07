import sqlite3
connection = sqlite3.connect("library.db")
cursor = connection.cursor()


cursor.execute(
    """ create table if not exists user(user_id integer primary key autoincrement,
    name text not null,
    email varchar not null,
    password text not null)"""

)

connection.commit()

cursor.execute(
    """ create table if not exists books(book_id integer primary key autoincrement,
    book_title text not null,
    author text not null,
    price float not null,
    stock integer not null)"""

)

connection.commit()


cursor.execute(
    """ create table if not exists cart_items(cart_id integer primary key autoincrement,
    user_id int not null,
    book_id int not null,
    qty integer not null,
    constraint user_id 
        foreign key(user_id) 
        references user(user_id) 
        on delete no action 
        on update no action,
    constraint book_id foreign key(book_id) 
        references books(book_id) 
        on delete no action 
        on update no action)"""

)



connection.commit()

cursor.execute("""create table if not exists orders(order_id integer primary key autoincrement,
               user_id int not null,
               order_date date not null,
               constraint user_id 
                foreign key(user_id) 
                references user(user_id) 
                on delete no action 
                on update no action)"""
)

connection.commit()

cursor.execute(
    """ create table if not exists order_items(order_item_id integer primary key autoincrement,
    order_id int not null,
    book_id int not null,
    qty integer not null,
    constraint order_id 
        foreign key(order_id) 
        references orders(order_id) 
        on delete no action 
        on update no action,
    constraint book_id 
        foreign key(book_id) 
        references books(book_id) 
        on delete no action 
        on update no action,
    constraint qty 
        foreign key(qty) 
        references cart_items(qty) 
        on delete no action 
        on update no action)"""

)



connection.commit()



cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrowed_books (
        borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        borrow_date TEXT NOT NULL,
        return_date TEXT,
        FOREIGN KEY(user_id) REFERENCES user(user_id),
        FOREIGN KEY(book_id) REFERENCES books(book_id)
    )
""")

connection.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

connection.commit()
connection.close()
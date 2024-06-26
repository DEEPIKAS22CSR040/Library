import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from psycopg2 import Error

app = Flask(__name__)
app.secret_key = 'abcxyz'

# Initialize global database connection
mydb = None

try:
    mydb = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="Deepika@2004",
        database="library",
        port=5432,
    )
    mycursor = mydb.cursor()
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255)
        )
    """)
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id SERIAL PRIMARY KEY,
            bname VARCHAR(255),
            bcategory VARCHAR(255),
            language VARCHAR(255),
            byear VARCHAR(255),
            bnumber VARCHAR(255)
        )
    """)
    mydb.commit()
    print("Connected to database and ensured 'users' and 'book' tables exist.")
except Exception as e:
    print(f"Error: {e}")

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/bp/<bid>', methods=['GET', 'POST'])
def bp(bid):
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        borrow_date = request.form.get('borrow_date')
        return_date = request.form.get('return_date')

        try:
            mycursor = mydb.cursor()
            mycursor.execute("""
                INSERT INTO borrowing (user_id, book_id, borrow_date, return_date)
                VALUES (%s, %s, %s, %s)
            """, (user_id, bid, borrow_date, return_date))
            mycursor.execute("""
                UPDATE book SET available = FALSE WHERE bid = %s
            """, (bid,))
            mydb.commit()
            flash('Book borrowed successfully!')
        except Exception as e:
            mydb.rollback()
            flash(f"Error borrowing book: {e}")
        finally:
            mycursor.close()

        return redirect(url_for('table1'))
    else:
        return render_template('bp.html', bid=bid)

@app.route('/student1', methods=['POST', 'GET'])
def student1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mycursor = None
        try:
            mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
            mycursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = mycursor.fetchone()
            if user:
                return render_template('index1.html')
            else:
                message = 'Please enter correct username / password!'
                return render_template('student.html', message=message), 401
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
    return render_template('student.html')

@app.route('/admin1', methods=['POST'])
def admin1():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mycursor = None
        try:
            mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
            mycursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = mycursor.fetchone()
            if user:
                return render_template('index.html')
            else:
                message = 'Please enter correct username / password!'
                return render_template('admin.html', message=message), 401
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
    return render_template('admin.html')

@app.route('/home', methods=['GET', 'POST'])
def admin_home():
    return render_template('home.html')

@app.route('/admin1', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/table1', methods=['GET', 'POST'])
def table1():
    mycursor = None
    book_dicts = []  # Initialize book_dicts to an empty list
    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("SELECT id, bname, bcategory, language, byear, bnumber FROM book")
        books = mycursor.fetchall()
        for book in books:
            book_dict = {
                'id': book[0],
                'bname': book[1],
                'bcategory': book[2],
                'language': book[3],
                'byear': book[4],
                'bnumber': book[5]
            }
            book_dicts.append(book_dict)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if mycursor:
            mycursor.close()
    return render_template('table1.html', books=book_dicts)

@app.route('/get', methods=['GET', 'POST'])
def get():
    bname = request.form.get('bname')
    bcategory = request.form.get('bcategory')
    language = request.form.get('language')
    byear = request.form.get('byear')
    bnumber = request.form.get('bnumber')
    print(bname)
    book = (bname, bcategory, language, byear, bnumber)
    print("Received values:", bname, bcategory, language, byear, bnumber)

    mycursor = None
    try:
        mycursor = mydb.cursor()
        mycursor.execute("""
            INSERT INTO book (bname, bcategory, language, byear, bnumber)
            VALUES (%s, %s, %s, %s, %s)
        """, book)
        mydb.commit()
        print("Record added to 'book' table")
        text = "0"
        return render_template('home.html', success=text)
    except Exception as e:
        text = "1"
        print("Error:", e)
        return render_template('home.html', success=text)
    finally:
        if mycursor:
            mycursor.close()

@app.route('/table', methods=['GET', 'POST'])
def table():
    mycursor = None
    book_dicts = []  # Initialize book_dicts to an empty list
    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("SELECT id, bname, bcategory, language, byear, bnumber FROM book")
        books = mycursor.fetchall()
        for book in books:
            book_dict = {
                'id': book[0],
                'bname': book[1],
                'bcategory': book[2],
                'language': book[3],
                'byear': book[4],
                'bnumber': book[5]
            }
            book_dicts.append(book_dict)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if mycursor:
            mycursor.close()
    return render_template('table.html', books=book_dicts)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    mycursor = None
    if request.method == 'GET':
        try:
            mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
            mycursor.execute("SELECT * FROM book WHERE id = %s", (id,))
            book = mycursor.fetchone()
            if book:
                book_dict = {
                    'id': book[0],
                    'bname': book[1],
                    'bcategory': book[2],
                    'language': book[3],
                    'byear': book[4],
                    'bnumber': book[5]
                }
                return render_template('edit.html', book=book_dict)
            else:
                return "Book not found", 404
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
    elif request.method == 'POST':
        bname = request.form.get('bname')
        bcategory = request.form.get('bcategory')
        language = request.form.get('language')
        byear = request.form.get('byear')
        bnumber = request.form.get('bnumber')
        mycursor = None
        try:
            mycursor = mydb.cursor()
            update_query = """
                UPDATE book
                SET bname = %s, bcategory = %s, language = %s, byear = %s, bnumber = %s
                WHERE id = %s
            """
            mycursor.execute(update_query, (bname, bcategory, language, byear, bnumber, id))
            mydb.commit()
        except Error as e:
            print(f"Error: {e}")
        finally:
            if mycursor:
                mycursor.close()
        return redirect('/table')

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    mycursor = None
    try:
        mycursor = mydb.cursor()
        mycursor.execute("DELETE FROM book WHERE id = %s", (id,))
        mydb.commit()
        print(f"Record with ID {id} deleted from 'books' table")
    except Error as e:
        print("Error:", e)
    finally:
        if mycursor:
            mycursor.close()
    return redirect('/table')


@app.route('/view_borrowed_books', methods=['GET'])
def view_borrowed_books():
    mycursor = None
    borrowed_books = []
    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("""
            SELECT b.bid, b.bname, b.bcategory, b.language, b.byear, a.author_name, a.description,
                   u.user_id, u.username
            FROM book b
            LEFT JOIN author a ON b.bid = a.bid
            LEFT JOIN borrowing br ON b.bid = br.book_id
            LEFT JOIN users u ON br.user_id = u.user_id
            WHERE br.returned = FALSE
        """)
        borrowed = mycursor.fetchall()
        for book in borrowed:
            borrowed_book = {
                'bid': book['bid'],
                'bname': book['bname'],
                'bcategory': book['bcategory'],
                'language': book['language'],
                'byear': book['byear'],
                'author_name': book['author_name'],
                'description': book['description'],
                'user_id': book['user_id'],
                'username': book['username']
            }
            borrowed_books.append(borrowed_book)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if mycursor:
            mycursor.close()
    return render_template('view_borrowed_books.html', books=borrowed_books)


@app.route('/view_available_books', methods=['GET'])
def view_available_books():
    mycursor = None
    available_books = []
    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("""
            SELECT b.bid, b.bname, b.bcategory, b.language, b.byear, a.author_name, a.description
            FROM book b
            LEFT JOIN author a ON b.bid = a.bid
            WHERE b.available = TRUE
        """)
        available = mycursor.fetchall()
        for book in available:
            available_book = {
                'bid': book['bid'],
                'bname': book['bname'],
                'bcategory': book['bcategory'],
                'language': book['language'],
                'byear': book['byear'],
                'author_name': book['author_name'],
                'description': book['description'],
            }
            available_books.append(available_book)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if mycursor:
            mycursor.close()
    return render_template('view_available_books.html', books=available_books)

@app.route('/search_books', methods=['GET'])
def search_books():
    mycursor = None
    category = request.args.get('category', '')

    try:
        mycursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)
        mycursor.execute("""
            SELECT b.bid, b.bname, b.bcategory, b.language, b.byear, a.author_name, a.description 
            FROM book b
            LEFT JOIN author a ON b.bid = a.bid 
            WHERE b.bcategory = %s
        """, (category,))
        books = mycursor.fetchall()
        return render_template('search_results.html', books=books, category=category)
    except psycopg2.Error as e:
        print("Error searching books:", e)
        return render_template('search_results.html', books=[], category=category)
    finally:
        if mycursor:
            mycursor.close()

if __name__ == '__main__':
    app.run(debug=True)


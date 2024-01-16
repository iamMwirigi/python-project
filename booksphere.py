from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import click
import os

Base = declarative_base()

# file paths
authors_file = 'authors.txt'
books_file = 'books.txt'
users_file = 'users.txt'
borrowed_books_file = 'borrowed_books.txt'

engine = create_engine('sqlite:///booksphere.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    books = relationship('Book', back_populates='author')


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship('Author', back_populates='books')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    borrowed_books = relationship('Book', secondary='borrowed_books')


class BorrowedBooks(Base):
    __tablename__ = 'borrowed_books'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))


def create_database():
    Base.metadata.create_all(engine)


def add_sample_data():
    author1 = Author(name="J.K. Rowling")
    author2 = Author(name="George Orwell")
    book1 = Book(title="Harry Potter", author=author1)
    book2 = Book(title="1984", author=author2)
    user1 = User(name="Alice")
    user2 = User(name="Bob")
    session.add_all([author1, author2, book1, book2, user1, user2])
    session.commit()


def search_books(keyword):
    books = session.query(Book).filter(Book.title.ilike(f'%{keyword}%')).all()
    return books


def add_user(name):
    new_user = User(name=name)
    session.add(new_user)
    session.commit()


def add_author(name):
    new_author = Author(name=name)
    session.add(new_author)
    session.commit()


def add_book(title, author_name):
    author = session.query(Author).filter_by(name=author_name).first()
    if author:
        new_book = Book(title=title, author=author)
        session.add(new_book)
        session.commit()
    else:
        print(f"Author '{author_name}' not found. Please add the author first.")


def borrow_book(user_name, book_title):
    user = session.query(User).filter_by(name=user_name).first()
    book = session.query(Book).filter_by(title=book_title).first()
    if user and book:
        user.borrowed_books.append(book)
        session.commit()
    else:
        print("User or book not found. Please check the user and book details.")


def load_data_from_files():
    for file_path, model in zip([authors_file, books_file, users_file, borrowed_books_file],
                                [Author, Book, User, BorrowedBooks]):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split('|')
                    instance = model(**{col: val for col, val in zip(model.__table__.columns.keys(), data)})
                    session.add(instance)
            session.commit()


def save_data_to_files():
    for file_path, model in zip([authors_file, books_file, users_file, borrowed_books_file],
                                [Author, Book, User, BorrowedBooks]):
        with open(file_path, 'w') as file:
            for instance in session.query(model).all():
                values = [str(getattr(instance, col)) for col in model.__table__.columns.keys()]
                line = '|'.join(values) + '\n'
                file.write(line)


@click.command()
def main():
    create_database()
    load_data_from_files()

    while True:
        click.echo("\nLibrary Management System")
        click.echo("1. Search Books")
        click.echo("2. Add User")
        click.echo("3. Add Author")
        click.echo("4. Add Book")
        click.echo("5. Borrow Book")
        click.echo("6. Save and Exit")
        choice = click.prompt("Enter your choice (1-6)", type=int)

        if choice == 1:
            keyword = click.prompt("Enter the keyword to search")
            books = search_books(keyword)
            if books:
                click.echo("\nSearch Results:")
                for book in books:
                    click.echo(f"{book.title} by {book.author.name}")
            else:
                click.echo("No books found.")
        elif choice == 2:
            name = click.prompt("Enter the user's name")
            add_user(name)
            click.echo(f"User '{name}' added successfully.")
        elif choice == 3:
            name = click.prompt("Enter the author's name")
            add_author(name)
            click.echo(f"Author '{name}' added successfully.")
        elif choice == 4:
            title = click.prompt("Enter the book's title")
            author_name = click.prompt("Enter the author's name")
            add_book(title, author_name)
            click.echo(f"Book '{title}' added successfully.")
        elif choice == 5:
            user_name = click.prompt("Enter the user's name")
            book_title = click.prompt("Enter the book's title")
            borrow_book(user_name, book_title)
            click.echo(f"Book '{book_title}' borrowed by '{user_name}'.")
        elif choice == 6:
            save_data_to_files()
            click.echo("Data saved. Exiting Library Management System. Goodbye!")
            break
        else:
            click.echo("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
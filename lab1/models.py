from datetime import datetime, date, timedelta
from typing import List, Optional

class Library:
    def __init__(self, id: int, name: str, address: str):
        self.id = id
        self.name = name
        self.address = address
        self.books: List[Book] = []
        self.librarians: List[Librarian] = []
    
    def add_book(self, book: 'Book'):
        self.books.append(book)
        print(f"Книга '{book.title}' добавлена")
    
    def remove_book(self, id: int):
        self.books = [b for b in self.books if b.id != id]
        print(f"Книга с ID {id} удалена")

class Book:
    def __init__(self, id: int, title: str, author: str, year: int):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.status = "доступна"
    
    def borrow(self):
        if self.status == "доступна":
            self.status = "Выдана"
            print(f"Книга '{self.title}' выдана")
        else:
            print(f"Книга '{self.title}' недоступна")
    
    def return_book(self):
        self.status = "доступна"
        print(f"Книга '{self.title}' возвращена")
    
    def get_info(self) -> str:
        return f"Книга ID: {self.id}, Название: '{self.title}', Автор: {self.author}, Статус: {self.status}"

class FictionBook(Book):
    def __init__(self, id: int, title: str, author: str, year: int, genre: str):
        if year <= 0:
            raise ValueError("Год издания должен быть положительным")
        super().__init__(id, title, author, year)
        self.genre = genre

class ScientificBook(Book):
    def __init__(self, id: int, title: str, author: str, year: int, field: str):
        if year <= 0:
            raise ValueError("Год издания должен быть положительным")
        super().__init__(id, title, author, year)
        self.field = field

class Textbook(Book):
    def __init__(self, id: int, title: str, author: str, year: int, subject: str):
        if year <= 0:
            raise ValueError("Год издания должен быть положительным")
        super().__init__(id, title, author, year)
        self.subject = subject

class Librarian:
    def __init__(self, id: int, name: str, employee_id: str):
        self.id = id
        self.name = name
        self.employee_id = employee_id
        self.managed_borrowings: List[Borrowing] = []

class Reader:
    def __init__(self, id: int, full_name: str, phone: str):
        self.id = id
        self.full_name = full_name
        self.phone = phone
        self.borrowings: List[Borrowing] = []
    
    def borrow_book(self, book: Book, librarian: Librarian, return_date: date) -> 'Выдача ':
        borrowing = Borrowing(len(self.borrowings) + 1, date.today(), return_date)
        borrowing.book = book
        borrowing.librarian = librarian
        self.borrowings.append(borrowing)
        librarian.managed_borrowings.append(borrowing)
        book.borrow()
        print(f"Книга '{book.title}' выдана читателю {self.full_name}")
        return borrowing
    
    def return_book(self, borrowing_id: int):
        for borrowing in self.borrowings:
            if borrowing.id == borrowing_id:
                borrowing.book.return_book()
                self.borrowings.remove(borrowing)
                print(f"Книга возвращена")
                return
        print(f"Выдача с ID {borrowing_id} не найдена")

class Borrowing:
    def __init__(self, id: int, borrow_date: date, return_date: date):
        self.id = id
        self.borrow_date = borrow_date
        self.return_date = return_date
        self.status = "доступна"
        self.book: Optional[Book] = None
        self.librarian: Optional[Librarian] = None
    
    def get_info(self) -> str:
        book_title = self.book.title if self.book else "Не назначена"
        librarian_name = self.librarian.name if self.librarian else "Не назначен"
        return f"Выдача ID: {self.id}, Книга: '{book_title}', Библиотекарь: {librarian_name}, Статус: {self.status}"

class LibrarySystem:
    def __init__(self):
        self.library = Library(1, "Центральная библиотека", "ул. Книжная, 1")
        self.readers: List[Reader] = []
        self.borrowings: List[Borrowing] = []
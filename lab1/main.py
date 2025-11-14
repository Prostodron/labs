from models import *
from data_manager import DataManager
from datetime import datetime, date, timedelta

if __name__ == "__main__":
    system = LibrarySystem()
    
    try:
        bad_book = FictionBook(10, "Плохая книга", "Автор", -2024, "фантастика")
    except ValueError as e:
        print(f"Ошибка: {e}")

    fiction_book = FictionBook(1, "Мастер и Маргарита", "Михаил Булгаков", 1966, "роман")
    scientific_book = ScientificBook(2, "Краткая история времени", "Стивен Хокинг", 1988, "физика")
    textbook = Textbook(3, "Python для начинающих", "Джон Смит", 2023, "программирование")
    system.library.books.extend([fiction_book, scientific_book, textbook])
    
    librarian = Librarian(1, "Петрова Анна", "LIB001")
    system.library.librarians.append(librarian)
    
    reader = Reader(1, "Иванов Сергей", "+79991234567")
    system.readers.append(reader)
    
    return_date = date.today() + timedelta(days=14)
    borrowing = reader.borrow_book(fiction_book, librarian, return_date)
    system.borrowings.append(borrowing)

    print("ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ")
    print(fiction_book.get_info())
    print(borrowing.get_info())
    
    print("\nСОХРАНЕНИЕ ДАННЫХ")
    DataManager.save_to_json(system, "library_system.json")
    DataManager.save_to_xml(system, "library_system.xml")

    print("\nЗАГРУЗКА ДАННЫХ")
    new_system = LibrarySystem()
    DataManager.load_from_json("library_system.json", new_system)
    
    print(f"Книг: {len(new_system.library.books)}")
    print(f"Библиотекарей: {len(new_system.library.librarians)}")
    print(f"Читателей: {len(new_system.readers)}")
    print(f"Выдач: {len(new_system.borrowings)}")
    
    if new_system.library.books:
        print(f"Первая книга: {new_system.library.books[0].get_info()}")
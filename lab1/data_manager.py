# data_manager.py
import json
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Dict, Any
from models import *
print()

class DataManager:
    @staticmethod
    def to_dict(system: 'LibrarySystem') -> Dict[str, Any]:
        """Конвертирует систему в словарь для JSON"""
        return {
            "library": {
                "id": system.library.id,
                "name": system.library.name,
                "address": system.library.address,
                "books": [DataManager._book_to_dict(b) for b in system.library.books],
                "librarians": [DataManager._librarian_to_dict(l) for l in system.library.librarians]
            },
            "readers": [DataManager._reader_to_dict(r) for r in system.readers],
            "borrowings": [DataManager._borrowing_to_dict(b) for b in system.borrowings]
        }
    
    @staticmethod
    def _book_to_dict(book: 'Book') -> Dict[str, Any]:
        """Конвертирует книгу в словарь"""
        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "status": book.status
        }
    
    @staticmethod
    def _librarian_to_dict(librarian: 'Librarian') -> Dict[str, Any]:
        return {
            "id": librarian.id,
            "name": librarian.name,
            "employee_id": librarian.employee_id,
            "managed_borrowings": [b.id for b in librarian.managed_borrowings]
        }
    
    @staticmethod
    def _reader_to_dict(reader: 'Reader') -> Dict[str, Any]:
        return {
            "id": reader.id,
            "full_name": reader.full_name,
            "phone": reader.phone,
            "borrowings": [b.id for b in reader.borrowings]
        }
    
    @staticmethod
    def _borrowing_to_dict(borrowing: 'Borrowing') -> Dict[str, Any]:
        return {
            "id": borrowing.id,
            "borrow_date": borrowing.borrow_date.isoformat(),
            "return_date": borrowing.return_date.isoformat(),
            "status": borrowing.status,
            "book_id": borrowing.book.id if borrowing.book else None,
            "librarian_id": borrowing.librarian.id if borrowing.librarian else None,
            "reader_id": None
        }
    
    @staticmethod
    def save_to_json(system: 'LibrarySystem', filename: str):
        """Сохраняет систему в JSON"""
        data = DataManager.to_dict(system)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"Данные сохранены в {filename}")
    
    @staticmethod
    def load_from_json(filename: str, system: 'LibrarySystem'):
        """Загружает систему из JSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        DataManager._load_from_dict(data, system)
        print(f"Данные загружены из {filename}")
    
    @staticmethod
    def save_to_xml(system: 'LibrarySystem', filename: str):
        """Сохраняет систему в XML"""
        root = ET.Element("library_system")
        
        # Библиотека
        library_elem = ET.SubElement(root, "library")
        library_elem.set("id", str(system.library.id))
        library_elem.set("name", system.library.name)
        library_elem.set("address", system.library.address)
        
        # Книги
        books_elem = ET.SubElement(library_elem, "books")
        for book in system.library.books:
            book_elem = ET.SubElement(books_elem, "book")
            book_elem.set("id", str(book.id))
            book_elem.set("title", book.title)
            book_elem.set("author", book.author)
            book_elem.set("year", str(book.year))
            book_elem.set("status", book.status)
        
        # Библиотекари
        librarians_elem = ET.SubElement(library_elem, "librarians")
        for librarian in system.library.librarians:
            librarian_elem = ET.SubElement(librarians_elem, "librarian")
            librarian_elem.set("id", str(librarian.id))
            librarian_elem.set("name", librarian.name)
            librarian_elem.set("employee_id", librarian.employee_id)
            
            borrowings_elem = ET.SubElement(librarian_elem, "managed_borrowings")
            for borrowing in librarian.managed_borrowings:
                ET.SubElement(borrowings_elem, "borrowing_id").text = str(borrowing.id)
        
        # Читатели
        readers_elem = ET.SubElement(root, "readers")
        for reader in system.readers:
            reader_elem = ET.SubElement(readers_elem, "reader")
            reader_elem.set("id", str(reader.id))
            reader_elem.set("full_name", reader.full_name)
            reader_elem.set("phone", reader.phone)
            
            borrowings_elem = ET.SubElement(reader_elem, "borrowings")
            for borrowing in reader.borrowings:
                ET.SubElement(borrowings_elem, "borrowing_id").text = str(borrowing.id)
        
        # Выдачи
        borrowings_elem = ET.SubElement(root, "borrowings")
        for borrowing in system.borrowings:
            borrowing_elem = ET.SubElement(borrowings_elem, "borrowing")
            borrowing_elem.set("id", str(borrowing.id))
            borrowing_elem.set("borrow_date", borrowing.borrow_date.isoformat())
            borrowing_elem.set("return_date", borrowing.return_date.isoformat())
            borrowing_elem.set("status", borrowing.status)
            
            if borrowing.book:
                ET.SubElement(borrowing_elem, "book_id").text = str(borrowing.book.id)
            if borrowing.librarian:
                ET.SubElement(borrowing_elem, "librarian_id").text = str(borrowing.librarian.id)
        
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        print(f"Данные сохранены в {filename}")
    
    @staticmethod
    def load_from_xml(filename: str, system: 'LibrarySystem'):
        """Загружает систему из XML"""
        tree = ET.parse(filename)
        root = tree.getroot()
        
        # Очистка данных
        system.library.books.clear()
        system.library.librarians.clear()
        system.readers.clear()
        system.borrowings.clear()
        
        # Загрузка библиотеки
        library_elem = root.find("library")
        system.library.id = int(library_elem.get("id"))
        system.library.name = library_elem.get("name")
        system.library.address = library_elem.get("address")
        
        # Загрузка книг
        for book_elem in library_elem.find("books"):
            book_id = int(book_elem.get("id"))
            title = book_elem.get("title")
            author = book_elem.get("author")
            year = int(book_elem.get("year"))
            
            book = Book(book_id, title, author, year)
            book.status = book_elem.get("status")
            system.library.books.append(book)
        
        # Временное хранение выдач
        temp_borrowings = {}
        for borrowing_elem in root.find("borrowings"):
            borrowing_id = int(borrowing_elem.get("id"))
            borrow_date = date.fromisoformat(borrowing_elem.get("borrow_date"))
            return_date = date.fromisoformat(borrowing_elem.get("return_date"))
            
            borrowing = Borrowing(borrowing_id, borrow_date, return_date)
            borrowing.status = borrowing_elem.get("status")
            system.borrowings.append(borrowing)
            temp_borrowings[borrowing_id] = borrowing
        
        # Загрузка библиотекарей
        for librarian_elem in library_elem.find("librarians"):
            librarian_id = int(librarian_elem.get("id"))
            name = librarian_elem.get("name")
            employee_id = librarian_elem.get("employee_id")
            
            librarian = Librarian(librarian_id, name, employee_id)
            
            for borrowing_id_elem in librarian_elem.find("managed_borrowings"):
                borrowing_id = int(borrowing_id_elem.text)
                if borrowing_id in temp_borrowings:
                    librarian.managed_borrowings.append(temp_borrowings[borrowing_id])
            
            system.library.librarians.append(librarian)
        
        # Загрузка читателей
        for reader_elem in root.find("readers"):
            reader_id = int(reader_elem.get("id"))
            full_name = reader_elem.get("full_name")
            phone = reader_elem.get("phone")
            
            reader = Reader(reader_id, full_name, phone)
            
            for borrowing_id_elem in reader_elem.find("borrowings"):
                borrowing_id = int(borrowing_id_elem.text)
                if borrowing_id in temp_borrowings:
                    reader.borrowings.append(temp_borrowings[borrowing_id])
            
            system.readers.append(reader)
        
        print(f"Данные загружены из {filename}")
    
    @staticmethod
    def _load_from_dict(data: Dict[str, Any], system: 'LibrarySystem'):
        """Загружает данные из словаря"""
        # Очистка данных
        system.library.books.clear()
        system.library.librarians.clear()
        system.readers.clear()
        system.borrowings.clear()
        
        # Загрузка библиотеки
        library_data = data["library"]
        system.library.id = library_data["id"]
        system.library.name = library_data["name"]
        system.library.address = library_data["address"]
        
        # Загрузка книг
        for book_data in library_data["books"]:
            book = Book(
                book_data["id"],
                book_data["title"],
                book_data["author"],
                book_data["year"]
            )
            book.status = book_data["status"]
            system.library.books.append(book)
        
        # Временное хранение выдач
        temp_borrowings = {}
        for borrowing_data in data["borrowings"]:
            borrowing = Borrowing(
                borrowing_data["id"],
                date.fromisoformat(borrowing_data["borrow_date"]),
                date.fromisoformat(borrowing_data["return_date"])
            )
            borrowing.status = borrowing_data["status"]
            system.borrowings.append(borrowing)
            temp_borrowings[borrowing.id] = borrowing
        
        # Загрузка библиотекарей
        for librarian_data in library_data["librarians"]:
            librarian = Librarian(
                librarian_data["id"],
                librarian_data["name"],
                librarian_data["employee_id"]
            )
            
            for borrowing_id in librarian_data["managed_borrowings"]:
                if borrowing_id in temp_borrowings:
                    librarian.managed_borrowings.append(temp_borrowings[borrowing_id])
            
            system.library.librarians.append(librarian)
        
        # Загрузка читателей
        for reader_data in data["readers"]:
            reader = Reader(
                reader_data["id"],
                reader_data["full_name"],
                reader_data["phone"]
            )
            
            for borrowing_id in reader_data["borrowings"]:
                if borrowing_id in temp_borrowings:
                    reader.borrowings.append(temp_borrowings[borrowing_id])
            
            system.readers.append(reader)
import tkinter as tk
from tkinter import messagebox, font
import random

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Сапер")
        
        # Настройки игры
        self.rows = 10
        self.cols = 10
        self.mines_count = 15
        self.tile_size = 35
        
        # Игровые переменные
        self.game_over = False
        self.first_click = True
        self.flags_count = 0
        self.revealed_count = 0
        
        # Создание поля
        self.create_widgets()
        
        # Начало новой игры
        self.new_game()
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        self.title_label = tk.Label(self.root, text="САПЕР", font=("Arial", 24, "bold"), fg="darkred")
        self.title_label.pack(pady=5)
        
        # Информационная панель
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        # Счетчик мин
        self.mines_label = tk.Label(info_frame, text=f"💣 {self.mines_count}", font=("Arial", 14),fg="red")
        self.mines_label.pack(side=tk.LEFT, padx=20)
        
        # Кнопка перезапуска
        self.restart_btn = tk.Button(info_frame, text="😊", command=self.new_game,font=("Arial", 14),bg="lightgray")
        self.restart_btn.pack(side=tk.LEFT, padx=20)
        
        # Счетчик флагов
        self.flags_label = tk.Label(info_frame, text=f"🚩 0", font=("Arial", 14),fg="blue")
        self.flags_label.pack(side=tk.LEFT, padx=20)
        
        # Игровое поле
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(pady=10)
        
        # Создаем кнопки поля
        self.buttons = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                btn = tk.Button(self.game_frame, width=2, height=1,font=("Arial", 10, "bold"),bg="lightgray",relief="raised")
                btn.grid(row=i, column=j, padx=1, pady=1)
                
                # Привязываем обработчики событий
                btn.bind("<Button-1>", lambda e, r=i, c=j: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=i, c=j: self.right_click(r, c))
                
                row.append(btn)
            self.buttons.append(row)
    
    def new_game(self):
        """Начать новую игру"""
        self.game_over = False
        self.first_click = True
        self.flags_count = 0
        self.revealed_count = 0
        
        # Сбрасываем смайлик
        self.restart_btn.config(text="RS")
        
        # Обновляем счетчики
        self.mines_label.config(text=f"💣 {self.mines_count}")
        self.flags_label.config(text=f"🚩 {self.flags_count}")
        
        # Инициализируем поле
        self.field = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Сбрасываем кнопки
        for i in range(self.rows):
            for j in range(self.cols):
                self.buttons[i][j].config(text="", bg="lightgray", fg="black",relief="raised",state="normal")
    
    def generate_mines(self, first_i, first_j):
        """Генерация мин после первого клика"""
        mines_placed = 0
        
        while mines_placed < self.mines_count:
            i = random.randint(0, self.rows - 1)
            j = random.randint(0, self.cols - 1)
            
            # Не ставим мину на первую нажатую клетку и вокруг неё
            if (i == first_i and j == first_j) or \
               abs(i - first_i) <= 1 and abs(j - first_j) <= 1:
                continue
            
            if self.field[i][j] != -1:  # -1 означает мину
                self.field[i][j] = -1
                mines_placed += 1
                
                # Обновляем счетчики мин вокруг
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if (0 <= ni < self.rows and 0 <= nj < self.cols and 
                            self.field[ni][nj] != -1):
                            self.field[ni][nj] += 1
    
    def left_click(self, i, j):
        """Обработка левого клика (открытие клетки)"""
        if self.game_over or self.flagged[i][j]:
            return
        
        # Генерируем мины после первого клика
        if self.first_click:
            self.generate_mines(i, j)
            self.first_click = False
        
        # Если нажали на мину
        if self.field[i][j] == -1:
            self.game_over = True
            self.restart_btn.config(text="😵")
            self.reveal_all_mines()
            messagebox.showinfo("Игра окончена", "Вы наступили на мину!")
            return
        
        # Открываем клетку
        self.reveal_cell(i, j)
        
        # Проверяем победу
        if self.revealed_count == self.rows * self.cols - self.mines_count:
            self.game_over = True
            self.restart_btn.config(text="😎")
            messagebox.showinfo("Поздравляем!", "Вы нашли все мины!")
    
    def reveal_cell(self, i, j):
        """Открывает клетку (рекурсивно для пустых клеток)"""
        if (i < 0 or i >= self.rows or j < 0 or j >= self.cols or 
            self.revealed[i][j] or self.flagged[i][j]):
            return
        
        self.revealed[i][j] = True
        self.revealed_count += 1
        
        # Отображаем содержимое клетки
        value = self.field[i][j]
        
        # Цвета для цифр
        colors = {
            1: "blue",
            2: "green",
            3: "red",
            4: "darkblue",
            5: "darkred",
            6: "cyan",
            7: "black",
            8: "gray"
        }
        
        if value == 0:
            self.buttons[i][j].config(text="", bg="white", relief="sunken")
        else:
            self.buttons[i][j].config(text=str(value), fg=colors.get(value, "black"),bg="white",relief="sunken")
        
        # Если клетка пустая, открываем соседей
        if value == 0:
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    self.reveal_cell(i + di, j + dj)
    
    def right_click(self, i, j):
        """Обработка правого клика (установка/снятие флага)"""
        if self.game_over or self.revealed[i][j]:
            return
        
        if self.flagged[i][j]:
            # Снимаем флаг
            self.flagged[i][j] = False
            self.flags_count -= 1
            self.buttons[i][j].config(text="", bg="lightgray")
        else:
            # Ставим флаг
            self.flagged[i][j] = True
            self.flags_count += 1
            self.buttons[i][j].config(text="🚩", fg="red", bg="lightgray")
        
        # Обновляем счетчик флагов
        self.flags_label.config(text=f"🚩 {self.flags_count}")
    
    def reveal_all_mines(self):
        """Показывает все мины при проигрыше"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.field[i][j] == -1:
                    self.buttons[i][j].config(text="💣", bg="red", fg="black")
                elif self.flagged[i][j] and self.field[i][j] != -1:
                    self.buttons[i][j].config(text="❌", bg="pink", fg="red")

def main():
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
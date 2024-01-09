import pygame
import sys
import random
import re
import os
from tkinter import Tk, Frame, Label, Entry, Button, messagebox
from tkinter import font as tkfont

class Game:
    def __init__(self):
        self.BOARD_SIZE = 5
        self.WINDOW_SIZE = self.BOARD_SIZE * 100
        pygame.init()
        self.window = pygame.display.set_mode((self.BOARD_SIZE * 100, self.BOARD_SIZE * 100))
        pygame.display.set_caption('Сиджа')
        self.board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.players = ['Игрок', 'Компьютер']
        self.colors = {'Игрок': (255, 255, 255), 'Компьютер': (0, 0, 0)}
        self.current_player = self.players[0]
        self.circles = {'Игрок': ((self.BOARD_SIZE*self.BOARD_SIZE)-1)/2, 'Компьютер': ((self.BOARD_SIZE*self.BOARD_SIZE)-1)/2}
        self.game_phase = 1
        self.winner = None
        self.lst_psn = None

    def draw_board(self):
        # Отрисовка игрового поля
        self.window.fill((128, 128, 128))
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                pygame.draw.rect(self.window, (255, 255, 255), pygame.Rect(i * 100, j * 100, 100, 100), 1)
                if self.board[i][j] is not None:
                    pygame.draw.circle(self.window, self.colors[self.board[i][j]], (i * 100 + 50, j * 100 + 50), 45)
                if self.lst_psn is not None and (i, j) == self.lst_psn:
                    pygame.draw.circle(self.window, (0, 0, 255), (i * 100 + 50, j * 100 + 50), 50, 5)

    def any_posible_movs(self, player):
        # Проверка на возможность хода для игрока
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == player:
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if 0 <= i + di < self.BOARD_SIZE and 0 <= j + dj < self.BOARD_SIZE and self.board[i + di][j + dj] is None:
                                return True
        return False

    def ai_turn(self, player):
        # Ход ИИ
        # Разграничение игроков для ИИ
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        if self.game_phase == 1:
            empty_cells = [(i, j) for i in range(self.BOARD_SIZE) for j in range(self.BOARD_SIZE) if
                           self.board[i][j] is None]
            if empty_cells:
                i, j = random.choice(empty_cells)
                if (i, j) != (
                self.BOARD_SIZE // 2, self.BOARD_SIZE // 2):  # ИИ не занимает центральную клетку в первой фазе игры
                    self.handle_turn(player, i, j)
        elif self.game_phase == 2:
            player_cells = [(i, j) for i in range(self.BOARD_SIZE) for j in range(self.BOARD_SIZE) if
                            self.board[i][j] == player]
            random.shuffle(player_cells)

            for i, j in player_cells:
                for di, dj in directions:
                    if 0 <= i + di < self.BOARD_SIZE and 0 <= j + dj < self.BOARD_SIZE and self.board[i + di][j + dj] is None:
                        # Проверка, что ход приведет к захвату
                        if 0 <= i + 2 * di < self.BOARD_SIZE and 0 <= j + 2 * dj < self.BOARD_SIZE and \
                                self.board[i + 2 * di][j + 2 * dj] == player:
                            self.handle_turn(player, i, j)
                            self.handle_turn(player, i + di, j + dj)
                            # Удаление захваченной фишки
                            self.board[i + 2 * di][j + 2 * dj] = None
                            return

            for i, j in player_cells:
                for di, dj in directions:
                    if 0 <= i + di < self.BOARD_SIZE and 0 <= j + dj < self.BOARD_SIZE and self.board[i + di][j + dj] is None:
                        self.handle_turn(player, i, j)
                        self.handle_turn(player, i + di, j + dj)
                        return

    def check_sidzha_winner(self):
        # Проверка на победителя в игре Сиджа
        if self.game_phase == 2:
            if not self.any_posible_movs('Игрок'):
                self.winner = 'Компьютер'
            elif not self.any_posible_movs('Компьютер'):
                self.winner = 'Игрок'

    def handle_turn(self, player, i, j):
        # Обработка хода
        opponent = self.players[0] if player == self.players[1] else self.players[1]
        if self.game_phase == 1:
            if self.board[i][j] is None and (i, j) != (self.BOARD_SIZE // 2, self.BOARD_SIZE // 2):
                self.board[i][j] = player
                self.circles[player] -= 1
                if self.circles['Игрок'] == 0 and self.circles['Компьютер'] == 0:
                    self.game_phase = 2
                    # Проверка, кто окружил центральную клетку
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if self.board[self.BOARD_SIZE // 2 + di][self.BOARD_SIZE // 2 + dj] == player:
                            self.current_player = player
                            break
                        elif self.board[self.BOARD_SIZE // 2 + di][self.BOARD_SIZE // 2 + dj] == opponent:
                            self.current_player = opponent
                            break
                else:
                    self.current_player = opponent
                self.lst_psn = None
        elif self.game_phase == 2:
            if self.lst_psn is not None and self.board[i][j] is None:
                old_i, old_j = self.lst_psn
                # Проверка, что фишка перемещается на одну клетку по горизонтали или вертикали
                if abs(old_i - i) + abs(old_j - j) == 1:
                    self.board[old_i][old_j] = None
                    self.board[i][j] = player
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if 0 <= i + di < self.BOARD_SIZE and 0 <= j + dj < self.BOARD_SIZE:
                            if self.board[i + di][j + dj] == opponent and \
                                                                                                               0 <= i + 2 * di < self.BOARD_SIZE and 0 <= j + 2 * dj < self.BOARD_SIZE and \
                                                                                                               self.board[i + 2 * di][
                                                                                                                   j + 2 * dj] == player:
                                self.board[i + di][j + dj] = None
                    self.lst_psn = None
                    self.check_sidzha_winner()
                    if self.winner is None:
                        self.current_player = opponent
            elif self.board[i][j] == player:
                self.lst_psn = (i, j)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.current_player == self.players[0]:
                    x, y = pygame.mouse.get_pos()
                    i, j = x // 100, y // 100
                    self.handle_turn(self.current_player, i, j)
                elif self.current_player == self.players[1]:
                    self.ai_turn(self.current_player)
            self.window.fill((0, 0, 0))
            self.draw_board()
            pygame.display.flip()
            if self.winner is not None:
                for i in range(self.BOARD_SIZE):
                    for j in range(self.BOARD_SIZE):
                        if self.board[i][j] == self.winner:
                            pygame.draw.circle(self.window, (0, 0, 255), (i * 100 + 50, j * 100 + 50), 50, 5)
                            if self.winner == "Игрок":
                                res = messagebox.askquestion("Результат", "Вы победили! Хотите начать игру заново?")
                            else:
                                res = messagebox.askquestion("Результат", "Вы проиграли! Хотите начать игру заново?")
                            if res == "yes":
                                self.board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
                                self.players = ['Игрок', 'Компьютер']
                                self.colors = {'Игрок': (255, 0, 0), 'Компьютер': (0, 255, 0)}
                                self.current_player = self.players[0]
                                self.circles = {'Игрок': ((self.BOARD_SIZE * self.BOARD_SIZE) - 1) / 2,
                                                'Компьютер': ((self.BOARD_SIZE * self.BOARD_SIZE) - 1) / 2}
                                self.game_phase = 1
                                self.winner = None
                                self.lst_psn = None
                            else:
                                pygame.display.flip()
                                pygame.time.wait(5000)
                                pygame.quit()
                                sys.exit()

class Authentication:
    def __init__(self):
        self.DATABASE_FILE = "БД.txt"
        self.show_password = False
        self.create_database_file()
        self.root = Tk()
        self.root.title("Вход и регистрация")
        self.window_width = 640
        self.window_height = 480
        self.center_window(self.root, self.window_width, self.window_height)

        self.font = tkfont.Font(family="Arial", size=12)


        self.main_frame = Frame(self.root)
        self.main_frame.pack(expand=True)
        self.frame = Frame(self.main_frame)
        self.frame.pack(pady=10,)

        self.label_username = Label(self.frame, text="Имя пользователя:", font=self.font)
        self.label_username.grid(row=0, column=0, pady=2, sticky="w")

        self.label_password = Label(self.frame, text="Пароль:", font=self.font)
        self.label_password.grid(row=1, column=0, pady=5, sticky="w")

        self.entry_username = Entry(self.frame, font=self.font)
        self.entry_username.grid(row=0, column=1)

        self.entry_password = Entry(self.frame, show="*", font=self.font)
        self.entry_password.grid(row=1, column=1)

        self.button_show_password = Button(self.frame, text="Показать пароль", font=self.font,
                                           command=self.toggle_password_visibility)
        self.button_show_password.grid(row=1, column=2, padx=5)

        self.button_register = Button(self.main_frame, text="Регистрация", font=self.font, command=self.register)
        self.button_register.pack(pady=5)

        self.button_login = Button(self.main_frame, text="Войти", font=self.font, command=self.login)
        self.button_login.pack(pady=5)

        self.root.mainloop()

    def create_database_file(self):
        if not os.path.isfile(self.DATABASE_FILE):
            with open(self.DATABASE_FILE, "w") as file:
                pass

    def validate_password(self, password):
        pattern = r'^[a-zA-Z0-9]+$'
        return re.match(pattern, password) is not None

    def is_username_available(self, username):
        with open(self.DATABASE_FILE, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "," in line:
                    stored_username, _ = line.strip().split(",")
                    if username == stored_username:
                        return False
        return True

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username and password:
            if len(password) >= 8:
                if self.validate_password(password):
                    if self.is_username_available(username):
                        with open(self.DATABASE_FILE, "a") as file:
                            file.write(f"{username},{password}\n")
                        messagebox.showinfo("Регистрация", "Регистрация успешна!")
                    else:
                        messagebox.showerror("Ошибка", "Имя пользователя уже занято.")
                else:
                    messagebox.showerror("Ошибка", "Пароль должен состоять только из цифр и латинских символов.")
            else:
                messagebox.showerror("Ошибка", "Пароль должен содержать минимум 8 символов.")
        else:
            messagebox.showerror("Ошибка", "Введите имя пользователя и пароль.")

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username and password:
            if len(password) >= 8:
                if self.validate_password(password):
                    with open(self.DATABASE_FILE, "r") as file:
                        lines = file.readlines()
                        for line in lines:
                            if "," in line:
                                stored_username, stored_password = line.strip().split(",")
                                if username == stored_username and password == stored_password:
                                    messagebox.showinfo("Авторизация", "Авторизация успешна! Добро пожаловать в игру Сиджа!")
                                    self.root.withdraw()  # Скрывает первое окно
                                    Game().run()
                                    return
                        messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")
                else:
                    messagebox.showerror("Ошибка", "Пароль должен состоять только из цифр и латинских символов.")
            else:
                messagebox.showerror("Ошибка", "Пароль должен содержать минимум 8 символов.")
        else:
            messagebox.showerror("Ошибка", "Введите имя пользователя и пароль.")

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.entry_password.config(show="")
            self.button_show_password.config(text="Скрыть пароль")
        else:
            self.entry_password.config(show="*")
            self.button_show_password.config(text="Показать пароль")

    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    Authentication()

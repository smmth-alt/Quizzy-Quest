from tkinter import *
from tkinter import messagebox
from quiz_data import quiz_questions
import random
from PIL import Image, ImageTk
import pygame

try:
    pygame.mixer.init()
    sound_system_ok = True
except pygame.error as e:
    print(f"Warning: Pygame Mixer failed to initialize. Sound effects are disabled. Error: {e}")
    sound_system_ok = False


THEME_COLOR = "#F5BFF5"
QUESTION_BG = "#EBAA7F"
BUTTON_BG = "#EBAA7F"
BUTTON_FG = "#2c3e50"

FONT_STYLE = "Vicenza"
PRIMARY_COLOR = "#3F2340"

MYFONT = (FONT_STYLE, 14, "bold")
QUESTION_FONT = (FONT_STYLE, 20)
SCORE_FONT = (FONT_STYLE, 12, "bold")


DIFFICULTY_LIVES = {
    "easy": 3,
    "medium": 2,
    "hard": 1
}


MAX_QUESTIONS = 15


def play_sound(filename):
    """Plays a short sound effect using pygame mixer, if initialized."""
    if not sound_system_ok:
        return
    try:
        sound = pygame.mixer.Sound(filename)
        sound.play()
    except pygame.error as e:
        print(f"Error playing sound {filename}: {e}")


def play_background_music(filename):
    """Starts background music loop using pygame mixer."""
    if not sound_system_ok:
        return
    try:

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Error loading/playing background music {filename}: {e}")


class QuizGame_UI:
    def __init__(self):
        self.high_scores = {"easy": 0, "medium": 0, "hard": 0}
        self.question_list = []
        self.current_q_index = 0
        self.score = 0
        self.lives_remaining = 0
        self.current_difficulty = None
        self.sound_system_ok = sound_system_ok
        self.is_quiz_active = False

        self.window = Tk()
        self.window.title("Quizzy Quest")
        self.window.geometry("550x600")
        self.window.config(bg=THEME_COLOR, padx=30, pady=30)
        self.window.resizable(False, False)
        self.center_window(550, 600)

        play_background_music("background_sfx.wav")


        self.label_score = Label(
            text=f"Score: {self.score}",
            bg=THEME_COLOR,
            fg=PRIMARY_COLOR,
            font=SCORE_FONT
        )

        self.label_lives = Label(
            text="",
            bg=THEME_COLOR,
            fg="yellow",
            font=SCORE_FONT
        )

        CANVAS_SIZE = 40
        CANVAS_PADDING = 5

        try:
            home_img = Image.open("home_icon.gif")
            home_img = home_img.resize((CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)
            self.home_icon_img = ImageTk.PhotoImage(home_img)

            self.home_canvas = Canvas(
                self.window,
                width=CANVAS_SIZE + CANVAS_PADDING,
                height=CANVAS_SIZE + CANVAS_PADDING,
                bg=THEME_COLOR,
                highlightthickness=0
            )
            self.home_canvas.create_image(
                (CANVAS_SIZE + CANVAS_PADDING) // 2,
                (CANVAS_SIZE + CANVAS_PADDING) // 2,
                image=self.home_icon_img
            )
            self.home_canvas.bind("<Button-1>", self.handle_home_click)
            self.home_canvas.place_forget()

        except (TclError, FileNotFoundError):
            print("Warning: 'home_icon.gif' not found or is not a valid image. Using a standard button as fallback.")
            self.home_canvas = Button(
                self.window,
                text="🏠",
                font=(FONT_STYLE, 16),
                bg=THEME_COLOR,
                fg="#7872B3",
                bd=0,
                activebackground=THEME_COLOR,
                activeforeground="#7872B3",
                command=lambda: [play_sound("click.wav"), self.handle_home_click(None)]
            )
            self.home_canvas.place_forget()

        self.question_display = Label(
            self.window,
            text="",
            wraplength=450,
            justify="center",
            bg=QUESTION_BG,
            fg="#2c3e50",
            font=QUESTION_FONT,
            height=8,
            width=30,
            bd=0,
            relief="flat"
        )
        self.question_display.grid(row=2, column=0, columnspan=2, pady=(0, 30))

        self.option_buttons = []
        for i in range(4):
            btn = Button(
                text=f"Option {i + 1}",
                font=MYFONT,
                width=18,
                bg=BUTTON_BG,
                fg=BUTTON_FG,
                bd=0,
                activebackground="#e0df9f",
                activeforeground=BUTTON_FG,
                command=lambda i=i: [play_sound("click.wav"), self.check_answer(i)]
            )
            self.option_buttons.append(btn)


        self.label_feedback = Label(
            text="",
            bg=THEME_COLOR,
            fg="#f1c40f",
            font=MYFONT
        )
        self.label_feedback.grid(row=6, column=0, columnspan=2, pady=15)


        self.play_again_btn = Button(
            text="SELECT DIFFICULTY:",
            font=MYFONT,
            bg="#f39c12",
            fg="white",
            bd=0,

            command=lambda: [play_sound("click.wav"), self.go_to_difficulty_selection()]
        )


        self.restart_btn = Button(
            text="PLAY AGAIN",
            font=SCORE_FONT,
            bg="#e74c3c",
            fg="white",
            bd=0,
            activebackground="#c0392b",
            activeforeground="white",

            command=lambda: [play_sound("click.wav"), self.restart_quiz()]
        )

        self.highscore_board = Label(
            self.window,
            text="",
            bg=THEME_COLOR,
            fg="#3F2340",
            font=SCORE_FONT,
            justify="left"
        )
        self.highscore_board.place_forget()


        self.current_difficulty_hs = Label(
            self.window,
            text="",
            bg=THEME_COLOR,
            fg="#3F2340",
            font=SCORE_FONT,
            justify="left"
        )
        self.current_difficulty_hs.place_forget()


        self.game_over_home_btn = Button(
            self.window,
            text="🏠 HOME",
            font=MYFONT,
            bg="#8DD2E0",
            fg="#3F2340",
            bd=0,
            activebackground="#2980b9",
            activeforeground="#3F2340",
            command=lambda: [play_sound("click.wav"), self.display_welcome_screen()]
        )
        self.game_over_home_btn.place_forget()


        self.back_quiz_btn = Button(
            self.window,
            text="⬅ BACK",
            font=MYFONT,
            bg="#7872B3",
            fg="white",
            bd=0,
            activebackground="#7872B3",
            activeforeground="white",

            command=lambda: [play_sound("click.wav"), self.go_to_difficulty_selection()]
        )

        self.display_welcome_screen()
        self.window.mainloop()


    def handle_home_click(self, event):
        """Handles the click event on the home icon canvas with a confirmation dialog."""
        play_sound("click.wav")


        if self.is_quiz_active:
            confirm = messagebox.askyesno(
                "Exit Quiz",
                "Are you sure you want to exit the current quiz and return to the main screen? Your current score will be lost."
            )
            if confirm:
                self.is_quiz_active = False  # Reset state
                self.display_welcome_screen()
        else:
            self.display_welcome_screen()  # If not active, just go home

    # --- CENTER WINDOW ---
    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def get_lives_stars(self):
        return "Lives: " + "⭐" * self.lives_remaining


    def hide_game_elements(self):
        for btn in self.option_buttons:
            btn.grid_forget()

        self.play_again_btn.grid_forget()
        self.restart_btn.grid_forget()
        self.label_feedback.config(text="")

        if hasattr(self, 'difficulty_buttons'):
            for btn in self.difficulty_buttons:
                btn.grid_forget()
        if hasattr(self, 'welcome_buttons'):
            for btn in self.welcome_buttons:
                btn.grid_forget()
        if hasattr(self, 'back_button'):
            self.back_button.grid_forget()

        if hasattr(self, 'instr_frame'):
            self.instr_frame.destroy()
        if hasattr(self, 'instr_back_btn'):
            self.instr_back_btn.grid_forget()

        self.current_difficulty_hs.place_forget()
        self.highscore_board.place_forget()

        self.home_canvas.place_forget()

        # Added to hide the quiz back button
        self.back_quiz_btn.place_forget()

        self.game_over_home_btn.place_forget()

        if hasattr(self, 'bg_label'):
            self.bg_label.destroy()

    # --- HIGH SCORE TEXT ---
    def get_highscore_text(self):
        return (
            f"High Scores:\n"
            f"Easy: {self.high_scores['easy']}\n"
            f"Medium: {self.high_scores['medium']}\n"
            f"Hard: {self.high_scores['hard']}"
        )


    def display_welcome_screen(self):
        self.hide_game_elements()
        self.current_difficulty = None
        self.is_quiz_active = False  # Ensure this is reset

        self.label_score.grid_forget()
        self.label_lives.grid_forget()


        try:
            start_img = Image.open("start_bg.jpg")
            start_img = start_img.resize((550, 600), Image.LANCZOS)
            self.start_bg_img = ImageTk.PhotoImage(start_img)

            self.bg_label = Label(self.window, image=self.start_bg_img)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            # Fallback if image not found
            self.bg_label = Label(self.window, text="Quizzy Quest", bg=THEME_COLOR)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.question_display.config(
                text="Quizzy Quest\nWelcome!",
                bg=THEME_COLOR,
                fg=PRIMARY_COLOR,
                font=(FONT_STYLE, 30, "bold")
            )
            self.question_display.grid(row=2, column=0, columnspan=2, pady=(0, 30))

        self.welcome_buttons = []

        play_btn = Button(
            text="PLAY",
            font=MYFONT,
            width=18,
            bg="#2ecc71",
            fg="white",
            bd=0,
            activebackground="#27ae60",
            activeforeground="white",
            # 🎵 Updated sound filename/call
            command=lambda: [play_sound("click.wav"), self.start_difficulty_selection()]
        )
        play_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.welcome_buttons.append(play_btn)

        instr_btn = Button(
            text="INSTRUCTIONS",
            font=MYFONT,
            width=18,
            bg="#3498DB",
            fg="white",
            bd=0,
            activebackground="#2980b9",
            activeforeground="white",
            # 🎵 Updated sound filename/call
            command=lambda: [play_sound("click.wav"), self.show_instructions()]
        )
        instr_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.welcome_buttons.append(instr_btn)


    def show_instructions(self):
        self.hide_game_elements()


        self.instr_frame = Frame(self.window, bg=THEME_COLOR)
        self.instr_frame.grid(row=2, column=0, columnspan=2, pady=(0, 30), sticky="ew")


        instr_title = Label(
            self.instr_frame,
            text="INSTRUCTION",
            font=QUESTION_FONT,
            bg=THEME_COLOR,
            fg=PRIMARY_COLOR
        )
        instr_title.pack(pady=(0, 15))


        instruction_text = (
            "Welcome to “Quizzy Quest”! The quiz game begins by allowing "
            "the player to choose a difficulty category: easy, medium, or hard. "
            f"Each quiz has a total of {MAX_QUESTIONS} questions.\n\n"  # Added max questions info
            "Lives per difficulty:\n"
            f"Easy: {DIFFICULTY_LIVES['easy']} lives\n"
            f"Medium: {DIFFICULTY_LIVES['medium']} lives\n"
            f"Hard: {DIFFICULTY_LIVES['hard']} lives\n\n"
            "GOOD LUCK!"
        )

        instr_label = Label(
            self.instr_frame,
            text=instruction_text,
            wraplength=450,
            justify="center",  # Centers the text block
            bg=QUESTION_BG,
            fg="#2c3e50",
            font=("Hussar bold", 12, "bold"),
            padx=10,
            pady=10
        )
        instr_label.pack(expand=True, fill="both")


        self.instr_back_btn = Button(
            self.window,
            text="⬅ BACK",
            font=MYFONT,
            width=20,
            bg="#7872B3",
            fg="white",
            bd=0,
            activebackground="#7872B3",
            activeforeground="white",
            # 🎵 Updated sound filename/call
            command=lambda: [play_sound("click.wav"), self.return_from_instructions()]
        )
        self.instr_back_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def return_from_instructions(self):
        if hasattr(self, 'instr_frame'):
            self.instr_frame.destroy()
        if hasattr(self, 'instr_back_btn'):
            self.instr_back_btn.grid_forget()
        self.display_welcome_screen()

    # --- DIFFICULTY SELECT ---
    def start_difficulty_selection(self):
        self.hide_game_elements()
        self.label_score.grid_forget()
        self.label_lives.grid_forget()
        self.display_difficulty_buttons()

    def display_difficulty_buttons(self):
        self.question_display.config(
            text="Select Difficulty:",
            bg=THEME_COLOR,
            fg=PRIMARY_COLOR,
            font=QUESTION_FONT
        )

        self.difficulty_buttons = []
        difficulties = ["EASY", "MEDIUM", "HARD"]
        color_map = {
            "EASY": {"bg": "#2ecc71", "active": "#27ae60"},
            "MEDIUM": {"bg": "#e67e22", "active": "#d35400"},
            "HARD": {"bg": "#e74c3c", "active": "#c0392b"}
        }

        for i, diff in enumerate(difficulties):
            colors = color_map.get(diff)
            btn = Button(
                text=diff,
                font=MYFONT,
                width=20,
                bg=colors["bg"],
                fg="white",
                bd=0,
                activebackground=colors["active"],
                activeforeground="white",
                # 🎵 Updated sound filename/call
                command=lambda d=diff.lower(): [play_sound("click.wav"), self.start_quiz(d)]
            )
            btn.grid(row=i + 3, column=0, columnspan=2, padx=10, pady=10)
            self.difficulty_buttons.append(btn)

        self.back_button = Button(
            text="⬅ BACK",
            font=MYFONT,
            width=20,
            bg="#7872B3",
            fg="white",
            bd=0,
            activebackground="#7872B3",
            activeforeground="white",
            # 🎵 Updated sound filename/call
            command=lambda: [play_sound("click.wav"), self.display_welcome_screen()]
        )
        self.back_button.grid(row=6, column=0, columnspan=2, padx=10, pady=(20, 10))

        self.highscore_board.config(text=self.get_highscore_text())
        self.highscore_board.place(x=370, y=0)

    # --- START QUIZ ---
    def start_quiz(self, difficulty):
        for btn in getattr(self, 'difficulty_buttons', []):
            btn.grid_forget()
        if hasattr(self, 'back_button'):
            self.back_button.grid_forget()

        self.current_difficulty = difficulty
        self.is_quiz_active = True  # Set quiz state to active

        # --- ADJUSTMENT START ---
        # Kinuha ang lahat ng tanong para sa difficulty na ito
        all_questions = quiz_questions.get(difficulty, [])
        # Hinalo ang mga tanong
        random.shuffle(all_questions)
        # Kinuha lang ang unang MAX_QUESTIONS (15) na tanong
        self.question_list = all_questions[:MAX_QUESTIONS]
        # --- ADJUSTMENT END ---

        self.current_q_index = 0
        self.score = 0

        self.lives_remaining = DIFFICULTY_LIVES.get(difficulty, 5)

        self.label_score.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.label_score.config(text=f"Score: {self.score}")

        self.label_lives.grid(row=1, column=0, sticky="w", pady=(0, 15))
        self.label_lives.config(text=self.get_lives_stars())

        self.current_difficulty_hs.config(
            text=f"High Score: {self.high_scores[difficulty]}"
        )
        self.current_difficulty_hs.place(x=320, y=3)
        self.highscore_board.place_forget()


        self.home_canvas.place(x=245 - 20, y=-5)

        # Place the quiz-specific back button
        self.back_quiz_btn.place(x=10, y=500)

        self.display_question()

    def display_question(self):
        for i in range(4):
            self.option_buttons[i].grid(row=3 + (i // 2), column=i % 2, padx=10, pady=8)

        self.label_feedback.config(text="")

        if self.current_q_index < len(self.question_list):
            current_q_data = self.question_list[self.current_q_index]
            self.question_display.config(text=current_q_data["question"], bg=QUESTION_BG, fg="#2c3e50")

            for i in range(4):
                self.option_buttons[i].config(
                    text=current_q_data["options"][i],
                    state=NORMAL,
                    bg=BUTTON_BG,
                    fg=BUTTON_FG
                )
        else:
            self.show_final_score()

    def check_answer(self, selected_option_index):
        for btn in self.option_buttons:
            btn.config(state=DISABLED)

        current_q_data = self.question_list[self.current_q_index]
        selected_answer = current_q_data["options"][selected_option_index]
        correct_answer = current_q_data["answer"]

        if selected_answer == correct_answer:
            self.score += 1
            self.question_display.config(bg="#2ecc71")
            self.label_feedback.config(text="Correct! ✅", fg="#2ecc71")
            # 🎵 Updated sound filename/call
            play_sound("correct.wav")
        else:
            self.lives_remaining -= 1
            self.label_lives.config(text=self.get_lives_stars())
            self.question_display.config(bg="#e74c3c")
            self.label_feedback.config(text=f"Wrong! Answer: {correct_answer} ❌", fg="#e74c3c")
            # 🎵 Updated sound filename/call
            play_sound("mistake.wav")

        self.label_score.config(text=f"Score: {self.score}")
        self.current_q_index += 1

        if self.lives_remaining <= 0:
            self.is_quiz_active = False
            self.update_high_score()
            self.window.after(1500, self.game_over)
        elif self.current_q_index >= len(self.question_list):
            self.is_quiz_active = False
            self.update_high_score()
            self.window.after(1500, self.show_final_score)
        else:
            self.window.after(1500, self.display_question)

    def update_high_score(self):
        current_hs = self.high_scores.get(self.current_difficulty, 0)
        if self.score > current_hs:
            self.high_scores[self.current_difficulty] = self.score

        self.current_difficulty_hs.config(
            text=f"{self.current_difficulty.capitalize()} High Score: {self.high_scores[self.current_difficulty]}"
        )

    def game_over(self):
        self.hide_game_elements()
        self.is_quiz_active = False

        self.label_score.config(text=f"Final Score: {self.score}", bg=THEME_COLOR, fg="#3F2340")
        self.label_score.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.label_score.lift()

        self.label_lives.config(text="")
        self.label_lives.lift()

        self.question_display.config(
            text=f"GAME OVER!\n"  
                 "You ran out of lives!",
            bg=THEME_COLOR ,
            fg=PRIMARY_COLOR

        )
        self.question_display.lift()

        self.highscore_board.config(text=self.get_highscore_text(), bg=THEME_COLOR)
        self.highscore_board.place(x=370, y=0)
        self.highscore_board.lift()

        self.game_over_home_btn.place(x=190, y=500)
        self.game_over_home_btn.lift()

        self.play_again_btn.grid(row=5, column=0, columnspan=2, pady=15)
        self.play_again_btn.lift()

        self.restart_btn.grid(row=6, column=0, columnspan=2, pady=5)
        self.restart_btn.lift()

    def show_final_score(self):
        self.hide_game_elements()
        self.is_quiz_active = False

        current_hs = self.high_scores.get(self.current_difficulty, 0)
        if self.score == current_hs and self.score > 0:
            self.question_display.config(bg="black")
            feedback_text = "✨ NEW HIGH SCORE! ✨"
        else:
            self.question_display.config(bg=THEME_COLOR)
            feedback_text = "Thanks for playing!"

        self.label_score.config(text=f"Final Score: {self.score}")
        self.label_lives.config(text="")

        self.question_display.config(
            text=f"QUIZ COMPLETE! Final Score: {self.score}",
            fg=PRIMARY_COLOR
        )

        self.current_difficulty_hs.place_forget()

        self.highscore_board.config(text=self.get_highscore_text())
        self.highscore_board.place(x=370, y=0)

        self.label_feedback.config(text=feedback_text, fg="#7872B3")

        self.play_again_btn.grid(row=3, column=0, columnspan=2, pady=15)
        self.restart_btn.grid(row=6, column=0, columnspan=2, pady=5)

        self.game_over_home_btn.place(x=10, y=540)

    def go_to_difficulty_selection(self):
        self.hide_game_elements()
        self.is_quiz_active = False
        self.start_difficulty_selection()

    def restart_quiz(self):
        self.play_again_btn.grid_forget()
        self.restart_btn.grid_forget()
        self.game_over_home_btn.place_forget()

        if self.current_difficulty:
            self.start_quiz(self.current_difficulty)


if __name__ == "__main__":
    quiz_ui = QuizGame_UI()
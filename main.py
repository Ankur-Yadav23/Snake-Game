from tkinter import *
import random
import mysql.connector as m
import tkinter.font as font
from tkinter import messagebox
from functools import partial
from tkinter import ttk

# Initialising Dimensions of Game
WIDTH = 500
HEIGHT = 500
SPEED = 200
SPACE_SIZE = 20
BODY_SIZE = 2
SNAKE = "#00FF00"
FOOD = "#FFFFFF"
BACKGROUND = "#000000"

mydatabase = m.connect(host="localhost", user="root", password="ankur", database="snakegamedb")
score = 0
direction = "right"


def show_leaderboard():
    # Create the main window
    window = Tk()
    window.title("Leaderboard")
    window.geometry("500x500")
    window.configure(bg="light grey")

    # Create a label for the title
    title_label = Label(window, text="Leaderboard", fg="red", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Query to Execute
    query1 = "SELECT NAME, SCORE FROM leaderboard ORDER BY SCORE DESC LIMIT 5"

    # Create a Treeview widget
    leaderboard_tree = ttk.Treeview(window)
    leaderboard_tree["columns"] = ("Name", "Score")

    # Style the Treeview widget
    style = ttk.Style(leaderboard_tree)
    style.theme_use("winnative")
    style.configure("Treeview", rowheight="30", font=("Times", 12), fieldbackground='white', background="light blue")
    style.configure("leaderboard_tree.heading", font=("Roman", 16, "bold"), fg="red")

    # Assign the width, and anchor to the respective column and heading
    leaderboard_tree.column("#0", width=50, anchor=CENTER)
    leaderboard_tree.column("Name", width=100, anchor=CENTER)
    leaderboard_tree.column("Score", width=100, anchor=CENTER)
    leaderboard_tree.heading("#0", text="Rank", anchor=CENTER)
    leaderboard_tree.heading("Name", text="Name", anchor=CENTER)
    leaderboard_tree.heading("Score", text="Score", anchor=CENTER)
    leaderboard_tree.pack()

    # Create a cursor object to interact with the database
    cursor = mydatabase.cursor()

    # Retrieve data from the database
    cursor.execute(query1)
    leaderboard_data = cursor.fetchall()

    # Insert data into the Treeview
    for i, (name, score) in enumerate(leaderboard_data, start=1):
        leaderboard_tree.insert("", "end", text=str(i), values=(name, score))

    # Close the database connection
    mydatabase.close()

    # Run the main window loop
    window.mainloop()


def start_game():
    myFont = font.Font(family='Helvetica', size=20)
    player_name = nameEntry.get()
    if len(player_name) == 0:
        messagebox.showinfo(title="Oops", message="Please enter your name")
    else:
        # Class to design the snake
        class Snake:
            def __init__(self):
                self.body_size = BODY_SIZE
                self.coordinates = []
                self.squares = []

                for i in range(0, BODY_SIZE):
                    self.coordinates.append([0, 0])

                for x, y in self.coordinates:
                    square = canvas.create_rectangle(x, y,
                                                     x + SPACE_SIZE, y + SPACE_SIZE,
                                                     fill=SNAKE,
                                                     tag="snake")
                    self.squares.append(square)

            # Class to design the food

        class Food:

            def __init__(self):
                x = random.randint(0,
                                   (WIDTH / SPACE_SIZE) - 1) * SPACE_SIZE
                y = random.randint(0,
                                   (HEIGHT / SPACE_SIZE) - 1) * SPACE_SIZE

                self.coordinates = [x, y]

                canvas.create_oval(x, y, x + SPACE_SIZE, y +
                                   SPACE_SIZE, fill=FOOD, tag="food")

            # Function to check the next move of snake

        def next_turn(snake, food):

            x, y = snake.coordinates[0]

            if direction == "up":
                y -= SPACE_SIZE
            elif direction == "down":
                y += SPACE_SIZE
            elif direction == "left":
                x -= SPACE_SIZE
            elif direction == "right":
                x += SPACE_SIZE

            snake.coordinates.insert(0, (x, y))

            square = canvas.create_rectangle(
                x, y, x + SPACE_SIZE,
                      y + SPACE_SIZE, fill=SNAKE)

            snake.squares.insert(0, square)

            if x == food.coordinates[0] and y == food.coordinates[1]:

                global score

                score += 1

                label.config(text="Points:{}".format(score))

                canvas.delete("food")

                food = Food()

            else:

                del snake.coordinates[-1]

                canvas.delete(snake.squares[-1])

                del snake.squares[-1]

            if check_collisions(snake):
                game_over()

            else:
                window.after(SPEED, next_turn, snake, food)

            # Function to control direction of snake

        def change_direction(new_direction):

            global direction

            if new_direction == 'left':
                if direction != 'right':
                    direction = new_direction
            elif new_direction == 'right':
                if direction != 'left':
                    direction = new_direction
            elif new_direction == 'up':
                if direction != 'down':
                    direction = new_direction
            elif new_direction == 'down':
                if direction != 'up':
                    direction = new_direction

            # function to check snake's collision and position

        def check_collisions(snake):

            x, y = snake.coordinates[0]

            if x < 0 or x >= WIDTH:
                return True
            elif y < 0 or y >= HEIGHT:
                return True

            for body_part in snake.coordinates[1:]:
                if x == body_part[0] and y == body_part[1]:
                    return True

            return False

        def write_to_database():
            # Get the data entered by the user
            Name = player_name
            Score = score

            # Create a cursor object to interact with the database
            cursor = mydatabase.cursor()

            # Insert the data into the database
            query = "INSERT INTO leaderboard (NAME, SCORE) VALUES (%s, %s)"
            values = (Name, Score)
            cursor.execute(query, values)

            # Commit the changes to the database
            mydatabase.commit()

            # Close the database connection
            mydatabase.close()

            # Function to control everything

        def game_over():
            write_to_database()
            canvas.delete(ALL)
            canvas.create_text(canvas.winfo_width() / 2,
                    canvas.winfo_height() / 2,
                    font=('consolas', 70),
                    text="GAME OVER", fill="red",
                    tag="gameover")


            # Display of Points Scored in Game

        label = Label(window, text="Points:{}".format(score),
                      font=('consolas', 20))
        label.pack()

        canvas = Canvas(window, bg=BACKGROUND,
                        height=HEIGHT, width=WIDTH)
        canvas.pack()

        window.update()

        window_width = window.winfo_width()
        window_height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        window.bind('<Left>',
                    lambda event: change_direction('left'))
        window.bind('<Right>',
                    lambda event: change_direction('right'))
        window.bind('<Up>',
                    lambda event: change_direction('up'))
        window.bind('<Down>',
                    lambda event: change_direction('down'))

        snake = Snake()
        food = Food()

        next_turn(snake, food)

        window.mainloop()


# window
window = Tk()
window.geometry('800x400')
window.title('Snake Game')

# name label and text entry box
nameLabel = Label(window, text="Player_Name", fg="#2a52be", font=("Helvetica", 15, "bold"))
nameLabel.pack(side="top", ipady=10)
nameEntry = Entry(window, bg="Peach Puff", font=("Helvetica", 14, "bold"))
nameEntry.pack(side="top", ipady=5, pady=5)

# start button
startButton = Button(window, text="Start_Game", bg="#4681f4", bd=3, command=start_game, activebackground="#dd7973",
                     font=("Helvetica", 15, "bold"))
startButton.pack(side="top", ipady=2, pady=4)

# Create the show leaderboard button
button = Button(window, text="Show Leaderboard", bg="Red", bd=3, command=show_leaderboard,
                activebackground="#dd7973", font=("Helvetica", 15, "bold"))
button.pack(pady=10, padx=20)

window.mainloop()

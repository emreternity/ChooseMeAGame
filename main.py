import os
import json
import random
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog

CONFIG = "config.json"

EXCLUDED = "excluded.json"

def saveDir(dirPath):
    with open(CONFIG, 'w') as file:
        json.dump({"directory": dirPath}, file)

def loadDir():
    if os.path.exists(CONFIG):
        with open(CONFIG, 'r') as file:
            data = json.load(file)
            return data.get("directory")
    return None

def saveExcluded(excludedGames):
    with open(EXCLUDED, 'w') as file:
        json.dump({"excluded": excludedGames}, file)

def loadExcluded():
    if os.path.exists(EXCLUDED):
        with open(EXCLUDED, 'r') as file:
            data = json.load(file)
            return set(data.get("excluded", []))
    return set()


class ScrollableGameFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.command = command
        self.buttons = []

    def add_game_button(self, game_name):
        button = ctk.CTkButton(
            self,
            text=game_name,
            fg_color="gray25",
            hover_color="gray35"
        )
        button.grid(row=len(self.buttons), column=0, padx=5, pady=2, sticky="ew")
        button.bind('<Double-Button-1>', lambda e: self.command(game_name))
        self.buttons.append(button)

    def clear_buttons(self):
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

class GameLauncherApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("CMAG - Choose Me A Game")
        self.window.geometry("1000x600")
        self.window.minsize(800, 400)
        
        self.window.grid_columnconfigure(0, weight=3)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)
        
        self._create_directory_frame()
        self._create_title_labels()
        self._create_game_frames()
        self._create_control_frame()
        
        self.directory = loadDir()
        self.excluded_games = loadExcluded()
        self.games = []
        
        if self.directory:
            self.dir_entry.insert(0, self.directory)
            self.refresh_games_list()

    def _create_directory_frame(self):
        self.dir_frame = ctk.CTkFrame(self.window)
        self.dir_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.dir_frame.grid_columnconfigure(1, weight=1)
        
        self.dir_label = ctk.CTkLabel(self.dir_frame, text="Game Directory:")
        self.dir_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.dir_entry = ctk.CTkEntry(self.dir_frame, width=400)
        self.dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.dir_button = ctk.CTkButton(self.dir_frame, text="Browse Directory", command=self.browse_directory)
        self.dir_button.grid(row=0, column=2, padx=5, pady=5)

    def _create_title_labels(self):
        title_style = {
            "font": ctk.CTkFont(size=16, weight="bold"),
            "fg_color": "gray25",
            "corner_radius": 6,
            "padx": 10,
            "pady": 5
        }
        
        self.available_title = ctk.CTkLabel(self.window, text="Chosen Games", **title_style)
        self.available_title.grid(row=1, column=0, padx=10, pady=(5,0), sticky="ew")
        
        self.excluded_title = ctk.CTkLabel(self.window, text="Excluded Games", **title_style)
        self.excluded_title.grid(row=1, column=1, padx=10, pady=(5,0), sticky="ew")

    def _create_game_frames(self):
        frame_style = {
            "command": self.toggle_game,
            "width": 200,
            "height": 400
        }
        
        self.games_frame = ScrollableGameFrame(self.window, **frame_style)
        self.games_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        self.excluded_frame = ScrollableGameFrame(self.window, **frame_style)
        self.excluded_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

    def _create_control_frame(self):
        self.control_frame = ctk.CTkFrame(self.window)
        self.control_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.control_frame.grid_columnconfigure(0, weight=1)
        
        self.cmag_button = ctk.CTkButton(
            self.control_frame,
            text="CMAG!",
            command=self.run_cmag,
            width=200,
            height=40
        )
        self.cmag_button.grid(row=0, column=0, padx=5, pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory(
            title="Select Games Directory",
            initialdir=self.directory if self.directory else os.path.expanduser("~")
        )
        if directory:
            self.dir_entry.delete(0, 'end')
            self.dir_entry.insert(0, directory)
            self.update_directory()

    def update_directory(self):
        directory = self.dir_entry.get()
        if os.path.isdir(directory):
            saveDir(directory)
            self.directory = directory
            self.refresh_games_list()
            messagebox.showinfo("Success", f"Directory updated to: {directory}")
        else:
            messagebox.showerror("Error", "Invalid directory path")

    def refresh_games_list(self):
        self.games = [f for f in os.listdir(self.directory) if f.endswith(('.lnk', '.url'))]
        self.window.after(10, self._update_game_lists)

    def _update_game_lists(self):
        self.games_frame.clear_buttons()
        self.excluded_frame.clear_buttons()
        
        for game in self.games:
            if game in self.excluded_games:
                self.excluded_frame.add_game_button(game)
            else:
                self.games_frame.add_game_button(game)

    def toggle_game(self, game_name):
        if game_name in self.excluded_games:
            self.excluded_games.remove(game_name)
        else:
            self.excluded_games.add(game_name)
        
        saveExcluded(list(self.excluded_games))
        self.refresh_games_list()

    def run_cmag(self):
        available_games = [g for g in self.games if g not in self.excluded_games]
        if available_games:
            selected_game = random.choice(available_games)
            shortcut_path = os.path.join(self.directory, selected_game)
            messagebox.showinfo("CMAG", f"Launching: {selected_game}")
            subprocess.run(['cmd', '/c', 'start', '', shortcut_path], shell=True)
        else:
            messagebox.showwarning("Warning", "No games available to launch")

    def run(self):
        self.window.mainloop()

def main():
    app = GameLauncherApp()
    app.run()

if __name__ == "__main__":
    main()
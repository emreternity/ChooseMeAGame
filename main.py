import os
import json
import random
import subprocess

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

def gameList(directory):
    games = [f for f in os.listdir(directory) if f.endswith(('.lnk', '.url'))]
    excludedGames = loadExcluded()

    while True:
        print("\nCurrent list of games:")
        for idx, shortcut in enumerate(games, 1):
            excluded_tag = " (Excluded)" if shortcut in excludedGames else ""
            print(f"{idx}. {shortcut}{excluded_tag}")

        user_input = input("\nEnter the number or name of the game to exclude/include a game, '808' to return to menu or '0' to CMAG: ")

        if user_input == '0':
            for idx, shortcut in enumerate(games, 1):
                excluded_tag = " (Excluded)" if shortcut in excludedGames else ""
                if excluded_tag == "":
                    print(f"{idx}. {shortcut}{excluded_tag}")
            userApprove = input("\nThese are the current games you've selected. Enter '1' to keep choosing or '0' again to confirm: ")
            if userApprove == '0':
                break
            elif userApprove == '1':
                continue

        if user_input.isdigit():
            index = int(user_input) - 1
            if int(user_input) == 808:
                return 808
            elif 0 <= index < len(games):
                shortcut = games[index]
                if shortcut in excludedGames:
                    excludedGames.remove(shortcut)
                    print(f"Game '{shortcut}' has been re-included.")
                else:
                    excludedGames.add(shortcut)
                    print(f"Game '{shortcut}' has been excluded.")
                saveExcluded(list(excludedGames))
            else:
                print("Invalid number, please try again.")
        elif isinstance(user_input,str):
            slnk = f"{user_input}.lnk"
            surl = f"{user_input}.url"
            if slnk in excludedGames:
                excludedGames.remove(slnk)
                print(f"Game '{user_input}' has been re-included.")
            elif surl in excludedGames:
                excludedGames.remove(surl)
                print(f"Game '{user_input}' has been re-included.")
            else:
                if slnk in games:
                    excludedGames.add(slnk)
                    print(f"Game '{user_input}' has been excluded.")
                elif surl in games:
                    excludedGames.add(surl)
                    print(f"Game '{user_input}' has been excluded.")
            saveExcluded(list(excludedGames))   

        else:
            print("Invalid choice")     

    return [s for s in games if s not in excludedGames]

def cmag(directory, games):
    if games:
        selected_shortcut = random.choice(games)
        shortcut_path = os.path.join(directory, selected_shortcut)
        print(f"Executing: {selected_shortcut}")
        subprocess.run(['cmd', '/c', shortcut_path], shell=True)
        exit()
    else:
        print("No games available to execute.")

def menu():
    while True:
        print("\nMenu:")
        print("1. CMAG")
        print("2. Edit Directory")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            directory = loadDir()
            if directory and os.path.isdir(directory):
                filtered_games = gameList(directory)
                if filtered_games == 808:
                    continue
                else:
                    cmag(directory, filtered_games)
            else:
                print("No valid directory found. Please set a directory first.")
        elif choice == '2':
            directory = input("Enter the new folder directory: ")
            if os.path.isdir(directory):
                saveDir(directory)
                print(f"Directory '{directory}' has been updated.")
            else:
                print(f"The directory '{directory}' does not exist. Please try again.")
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

def main():
    saved_directory = loadDir()
    if not saved_directory:
        directory = input("Enter the folder directory: ")
        if os.path.isdir(directory):
            saveDir(directory)
            print(f"Directory '{directory}' has been saved.")
        else:
            print(f"The directory '{directory}' does not exist. Please try again.")
    menu()

if __name__ == "__main__":
    main()
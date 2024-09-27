import os
from pyrogram import Client
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, BadRequest

# Hardcoded API credentials (Replace with your actual API ID and API hash)
API_ID = 26955139  # Replace with your API ID
API_HASH = "147f0192ef238f2730ae6714f94072a9"  # Replace with your API hash


# Function to create a single session with a user-defined name
def create_session(session_name, save_dir):
    try:
        # Create a path for the session file
        session_file_path = os.path.join(save_dir, f"{session_name}")

        # Create a new session with the specified name
        app = Client(session_file_path, api_id=API_ID, api_hash=API_HASH)

        # Start the session and stop immediately after creation to save the session file
        with app:
            print(f"Session file for {session_name} created at {session_file_path}")

        return session_file_path

    except ApiIdInvalid:
        print(f"Error: Invalid API ID or API hash for session '{session_name}'. Skipping.")
    except ApiIdPublishedFlood:
        print(f"Error: Too many requests from this API ID for session '{session_name}'. Skipping.")
    except BadRequest as e:
        print(f"Error: {e} occurred for session '{session_name}'. Skipping.")
    except Exception as e:
        print(f"An unexpected error occurred for session '{session_name}': {e}. Skipping.")

# Function to create multiple sessions with predefined names
def create_multiple_sessions(session_names, save_dir):
    for session_name in session_names:
        create_session(session_name, save_dir)

# Function to safely get a valid integer input from the user
def get_valid_integer(prompt):
    while True:
        user_input = input(prompt)
        try:
            value = int(user_input)
            return value
        except ValueError:
            print("Error: Please enter a valid number.")

# Main function for handling the session creation process
def main():
    try:
        # Ask the user for the number of sessions (with input validation)
        session_count = get_valid_integer("Enter the number of sessions to create: ")

        # Ask the user for all session names at once
        session_names = []
        print("Enter the names for each session:")
        for i in range(session_count):
            session_name = input(f"Name for session {i + 1}: ")
            session_names.append(session_name)

        # Ask for the directory to save the session files
        save_dir = input("Enter the directory to save session files (default: 'sessions'): ") or "sessions"

        # Create the save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Create multiple sessions using the provided names
        create_multiple_sessions(session_names, save_dir)

        print(f"\nAll {session_count} session files have been processed.")
        print(f"Session files are saved in: {os.path.abspath(save_dir)}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}. The script will now exit.")

if __name__ == "__main__":
    main()
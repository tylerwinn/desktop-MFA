import os
import flet as ft
from utils.tokens import TokenManager
from utils.gui import build_login_screen, build_main_screen

# File to store the authentication state
AUTH_STATE_FILE = 'auth_state.txt'

def is_user_authenticated():
    # Check if the file exists and read the authentication state
    if os.path.exists(AUTH_STATE_FILE):
        with open(AUTH_STATE_FILE, 'r') as file:
            return file.read() == 'True'
    return False

def set_user_authenticated(authenticated):
    # Write the authentication state to the file
    with open(AUTH_STATE_FILE, 'w') as file:
        file.write(str(authenticated))

def main(page: ft.Page):
    print("Main function called")
    if not hasattr(page, "token_manager"):
        print("Initializing token_manager")
        page.token_manager = None

    def get_accounts():
        return page.token_manager.get_accounts() if page.token_manager else []

    def show_account_details(account_name: str):
        print(f"Show details for {account_name}")
        account_details = page.token_manager.generate_token(account_name)
        print(f"Token for {account_name}: {account_details}")

    def on_login(password: str):
        print("Attempting login")
        page.token_manager = TokenManager(password)

        if not page.token_manager.storage.decrypted:
            print("Login failure")
            set_user_authenticated(False)
        else:
            print("Login success")
            set_user_authenticated(True)
            change_route("/main")

    def change_route(route: str):
        print(f"Changing route to {route}")
        page.views.clear()
        if route == "/" and not is_user_authenticated():
            print("Loading login screen")
            page.views.append(ft.View(route="/", controls=build_login_screen(on_login)))
        elif route == "/main" and is_user_authenticated():
            print("Loading main screen")
            main_controls = build_main_screen(get_accounts(), show_account_details)
            page.views.append(ft.View(route="/main", controls=main_controls))

        page.update()

    page.on_route_change = change_route

    # Apply your page styling here
    page.title = "Authy Clone"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_height = 610
    page.window_width = 350
    page.window_resizable = False
    page.theme = ft.Theme(color_scheme_seed="green")

    # Determine initial view based on authentication status
    if not is_user_authenticated():
        print("Routing to login due to unauthenticated status")
        change_route("/")
    else:
        print("Routing to main due to authenticated status")
        change_route("/main")

if __name__ == "__main__":
    ft.app(target=main)

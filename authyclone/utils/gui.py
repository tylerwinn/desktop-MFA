import flet as ft

def build_login_screen(on_login):
    login_input = ft.TextField(label="Enter your password", password=True, can_reveal_password=True, width=300)
    login_button = ft.FilledTonalButton(text="Decrypt", on_click=lambda e: on_login(login_input.value))

    # Return the controls as a list
    return [login_input, login_button]

def build_main_screen(accounts, on_account_tap):
    print("Building main screen...")
    account_list = ft.ListView()

    for account in accounts:
        print(f"Adding account: {account}")
        def make_on_tap(account):
            return lambda e: on_account_tap(account)

        list_tile = ft.ListTile(
            #leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
            title=ft.Text(account),
            subtitle=ft.Text("Tap to view details"),
            on_click=make_on_tap(account)
        )
        account_list.controls.append(list_tile)
        print(f"Added account: {account}")

    print("Main screen built successfully.")
    return [account_list]


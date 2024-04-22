from kivy.config import Config
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '610')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from utils.tokens import TokenManager, TokenGenerator
from kivy.clock import Clock
from datetime import datetime

class AccountButton(Button):
    def __init__(self, **kwargs):
        super(AccountButton, self).__init__(**kwargs)
        self.register_event_type('on_long_press')
        self.bind(on_press=self.on_press_callback)
        self.bind(on_release=self.on_release_callback)
        self.long_press_time = 1  # time in seconds to recognize a long press
        self.long_press_event = None

    def on_press_callback(self, *args):
        self.long_press_event = Clock.schedule_once(self.trigger_long_press, self.long_press_time)

    def on_release_callback(self, *args):
        if self.long_press_event:
            self.long_press_event.cancel()

    def trigger_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *args):
        pass

class PasswordPopup(Popup):
    def check_password(self, password):
        app = App.get_running_app()
        try:
            app.token_manager = TokenManager(password)
        except ValueError:
            self.ids.error_label.text = "Bad password..."
            return
        self.dismiss()
        app.main_screen.populate_accounts()

class RenamePopup(Popup):
    def __init__(self, account_name, **kwargs):
        super(RenamePopup, self).__init__(**kwargs)
        self.account_name = account_name
        self.title = 'Rename Account'
        self.size_hint = (None, None)
        self.size = (300, 200)

        layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
        self.text_input = TextInput(text=self.account_name, multiline=False, size_hint_y=None, height=30)
        confirm_btn = Button(text='Confirm', size_hint_y=None, height=50)

        confirm_btn.bind(on_release=self.confirm_rename)
        layout.add_widget(Label(text='Enter new account name:'))
        layout.add_widget(self.text_input)
        layout.add_widget(confirm_btn)
        self.add_widget(layout)

    def confirm_rename(self, instance):
        new_name = self.text_input.text.strip()
        if new_name and new_name != self.account_name:
            token_manager = App.get_running_app().token_manager
            secret = token_manager.generators.pop(self.account_name).secret  # Extract secret
            token_manager.storage.remove_secret(self.account_name)  # Remove old name
            token_manager.add_secret(new_name, secret)  # Add with new name
            App.get_running_app().main_screen.populate_accounts()
        self.dismiss()

class AccountActionPopup(Popup):
    def __init__(self, account_name, **kwargs):
        super(AccountActionPopup, self).__init__(**kwargs)
        self.account_name = account_name
        self.title = 'Account Actions'
        self.size_hint = (None, None)
        self.size = (300, 200)

        layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
        delete_btn = Button(text='Delete')
        rename_btn = Button(text='Rename')
        
        delete_btn.bind(on_release=self.confirm_delete)
        rename_btn.bind(on_release=self.start_rename)

        layout.add_widget(Label(text=f'Actions for {account_name}:'))
        layout.add_widget(rename_btn)
        layout.add_widget(delete_btn)
        self.add_widget(layout)

    def confirm_delete(self, instance):
        App.get_running_app().token_manager.remove_secret(self.account_name)
        App.get_running_app().main_screen.populate_accounts()
        self.dismiss()

    def start_rename(self, instance):
        self.dismiss()
        rename_popup = RenamePopup(self.account_name)
        rename_popup.open()

class AddAccountPopup(Popup):
    def __init__(self, **kwargs):
        super(AddAccountPopup, self).__init__(**kwargs)
        self.title = 'Add New Account'
        self.size_hint = (0.9, 0.5)  # Use size_hint for relative sizing

        layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=1, padding=[10, 10, 10, 10])
        self.account_name_input = TextInput(multiline=False, size_hint_y=None, height=30, hint_text="Account Name")
        self.secret_input = TextInput(multiline=False, size_hint_y=None, height=30, hint_text="Secret")

        button_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)  # Grid layout for buttons
        save_btn = Button(text='Save', size_hint_y=None)
        cancel_btn = Button(text='Cancel', size_hint_y=None)

        # Bind buttons to their callbacks
        save_btn.bind(on_release=self.save_account)
        cancel_btn.bind(on_release=self.dismiss_popup)

        # Add widgets to layouts
        layout.add_widget(self.account_name_input)
        layout.add_widget(self.secret_input)
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        
        layout.add_widget(button_layout)  # Add button layout to the main layout
        self.add_widget(layout)

    def save_account(self, instance):
        account_name = self.account_name_input.text.strip()
        secret = self.secret_input.text.strip()
        if account_name:
            if not secret:  # Generate a secret if none was entered
                secret = TokenGenerator.generate_secret()
            App.get_running_app().token_manager.add_secret(account_name, secret)
            App.get_running_app().main_screen.populate_accounts()
        self.dismiss()

    def generate_secret(self, instance):
        self.secret_input.text = TokenGenerator.generate_secret()

    def dismiss_popup(self, instance):
        self.dismiss()


class MainScreen(BoxLayout):
    selected_account = None

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.update_countdown()  # Initialize the countdown immediately
        add_account_btn = Button(text='Add Account', size_hint_y=None, height=40, background_color=[0, 0.2, 0.4, 1])
        add_account_btn.bind(on_press=lambda instance: self.show_add_account_popup(instance))
        self.ids.accounts_layout.add_widget(add_account_btn)

    def populate_accounts(self):
        accounts_layout = self.ids.accounts_layout
        accounts_layout.clear_widgets()
        for account in App.get_running_app().token_manager.get_accounts():
            account_button = AccountButton(text=account, size_hint_y=None, height=40, background_color=[0, 0.2, 0.4, 1])
            account_button.bind(on_press=self.select_account)
            account_button.bind(on_long_press=lambda instance: self.show_account_actions(instance.text))
            accounts_layout.add_widget(account_button)

    def select_account(self, instance):
        self.selected_account = instance.text
        self.update_token_display()

    def show_add_account_popup(self, instance):
        popup = AddAccountPopup()
        popup.open()

    def show_account_actions(self, account_name):
        popup = AccountActionPopup(account_name)
        popup.open()

    def update_token_display(self):
        if App.get_running_app().token_manager and self.selected_account:
            try:
                token = App.get_running_app().token_manager.generate_token(self.selected_account)
                self.ids.token_label.text = token
            except ValueError:
                self.ids.token_label.text = "Error: Token not found"
        self.update_countdown()

    def update_countdown(self):
        # Schedule the update for every second
        Clock.schedule_interval(self.refresh_countdown, 1)

    def refresh_countdown(self, dt):
        time_left = 30 - datetime.now().second % 30
        self.ids.progress_bar.value = time_left
        self.ids.countdown_label.text = f"{time_left} sec(s)"
        if time_left == 30:
            self.update_token_display()  # Refresh token every 30 seconds

class TokenApp(App):
    token_manager = None
    main_screen = None

    def build(self):   
        self.main_screen = MainScreen()
        return self.main_screen

    def on_start(self):
        Clock.schedule_once(self.show_password_popup, 0.5)

    def show_password_popup(self, dt):
        PasswordPopup().open()

if __name__ == '__main__':
    TokenApp().run()

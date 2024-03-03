import customtkinter as ct
from utils.tokens import OTPGenerator
from utils.encryption import EncryptionHandler
import os

class AccountsFrame(ct.CTkScrollableFrame):
    def __init__(self, master, update_label, encryption_handler=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.update_label = update_label
        self.encryption_handler = encryption_handler 
        self.buttons = {}  # To keep track of buttons for deletion
        self.otp_generators = {}  # To store OTPGenerator instances

        # Bind right-click context menu to frame
        self.bind("<Button-3>", self.show_context_menu)

        # Add New Token button inside the scrollable frame, makes it add a new button when clicked
        add_token_btn = ct.CTkButton(self, text='Add New Token', command=self.add_account)
        add_token_btn.pack(side='bottom', fill='x', padx=20, pady=10)

    def select_account(self, account_name):
        # Retrieve the associated OTPGenerator instance
        otp_generator = self.otp_generators.get(account_name)
        if otp_generator:
            # Generate OTP using the associated OTPGenerator instance and update the label
            generated_otp = otp_generator.generate_otp()
            if generated_otp:
                self.update_label(generated_otp)
            else:
                # Handle error if OTP generation fails
                self.update_label("Error generating OTP")
        else:
            # Handle error if no associated OTPGenerator instance found
            self.update_label("No associated OTPGenerator instance found")

    def on_button_right_click(self, event, account_name):
        self.context_menu.tk_popup(event.x_root, event.y_root)
        self.account_to_delete = account_name  # Track which account to delete

    def delete_button(self):
        if self.account_to_delete in self.buttons:
            self.buttons[self.account_to_delete].destroy()  # Remove the button widget
            del self.buttons[self.account_to_delete]  # Remove the button from the dictionary

    def add_account(self):
        self.pack_forget()
        self.update_label('Add Account')
        # Check if encryption_handler is initialized
        if self.encryption_handler is not None:
            add_account_frame = AddNewAccountFrame(self.master, self.create_account_button, self.repack_accounts_frame, self.update_label, self.encryption_handler)
            add_account_frame.pack(fill='both', expand=True)
        else:
            self.update_label('Encryption handler not initialized')

    def repack_accounts_frame(self):
        self.pack(fill='both', expand=True)  # Repack the accounts frame with fill and expand


    def create_account_button(self, account_name, secret_key):
        btn = ct.CTkButton(self, text=account_name, command=lambda: self.select_account(account_name))
        btn.pack(fill='x', padx=20, pady=10)
        btn.bind("<Button-3>", lambda event, acc=account_name: self.on_button_right_click(event, acc))
        self.buttons[account_name] = btn  # Store the new button
        self.otp_generators[account_name] = OTPGenerator(secret_key)  # Store the OTPGenerator instance

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

class AddNewAccountFrame(ct.CTkFrame):
    def __init__(self, master, on_accept, on_decline, update_label, encryption_handler, **kwargs):
        super().__init__(master, **kwargs)
        self.on_accept = on_accept
        self.on_decline = on_decline
        self.update_label = update_label
        self.encryption_handler = encryption_handler  # Use the encryption handler passed from the App

        # Nickname Entry
        nickname_label = ct.CTkLabel(self, text="Nickname", font=("Roboto", 18))
        nickname_label.pack(pady=(10, 2))
        self.nickname_entry = ct.CTkEntry(self, placeholder_text="Nickname")
        self.nickname_entry.pack(pady=(2, 20))

        # Secret Entry
        secret_label = ct.CTkLabel(self, text="Secret", font=("Roboto", 18))
        secret_label.pack(pady=(10, 2))
        self.secret_entry = ct.CTkEntry(self, placeholder_text="Secret")
        self.secret_entry.pack(pady=(2, 20))

        # Accept Button
        accept_button = ct.CTkButton(self, text="Accept", command=self.accept)
        accept_button.pack(pady=10)

        # Decline Button
        decline_button = ct.CTkButton(self, text="Decline", command=self.decline)
        decline_button.pack(pady=10)

    def accept(self):
        nickname = self.nickname_entry.get()
        secret = self.secret_entry.get()
        if nickname and secret:
            if nickname in self.master.accounts_frame.buttons:
                error_label = ct.CTkLabel(self, text="Nickname already in use...", text_color='red')
                error_label.pack(pady=(10, 0))
            else:
                # Encrypt the secret key
                encrypted_secret = self.encryption_handler.encrypt(secret)

                # Store the encrypted secret in a file named after the account nickname
                with open(f"{nickname}_secret.bin", "wb") as file:
                    file.write(encrypted_secret)

                # Notify the main application to create a button for the new account
                self.on_accept(nickname, secret)  # You may want to pass encrypted_secret instead
                self.pack_forget()  # Hide this frame
                self.on_decline()  # Repack and show the accounts frame
        else:
            error_label = ct.CTkLabel(self, text="Please enter both nickname and secret", text_color='red')
            error_label.pack(pady=(10, 0))

    def decline(self):
        self.pack_forget()
        self.update_label('Hello, world!')
        self.on_decline()

class PasswordFrame(ct.CTkFrame):
    def __init__(self, master, on_password_accept, **kwargs):
        super().__init__(master, **kwargs)
        self.on_password_accept = on_password_accept  # Callback function when password is accepted

        # Password Entry
        password_label = ct.CTkLabel(self, text="Password", font=("Roboto", 18))
        password_label.pack(pady=(10, 2))
        self.password_entry = ct.CTkEntry(self, placeholder_text="Password", show='*')  # Masked input
        self.password_entry.pack(pady=(2, 20))

        # Accept Button
        accept_button = ct.CTkButton(self, text="Login", command=self.accept)
        accept_button.pack(pady=10)

    def accept(self):
        password = self.password_entry.get()
        if password:
            # If a password is entered, invoke the callback with the password
            self.on_password_accept(password)
            self.pack_forget()  # Hide this frame after successful login
        else:
            # Show an error message if the password field is empty
            error_label = ct.CTkLabel(self, text="Please enter a password", text_color='red')
            error_label.pack(pady=(10, 0))

    def decline(self):
        self.pack_forget()  # Hide this frame

class App(ct.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('350x610')
        ct.set_appearance_mode('dark')  # Set appearance mode
        ct.set_default_color_theme('dark-blue')  # Set color theme

        self.encryption_handler = None # Will be initialized after password is accepted

        self.code_display = ct.CTkLabel(self, text='Login, please!', font=('Roboto', 40))
        self.code_display.pack(pady=20, padx=20)

        self.accounts_frame = AccountsFrame(self, self.update_code_display, self.encryption_handler)
        self.password_frame = PasswordFrame(self, self.on_password_accepted)
        self.password_frame.pack(fill='both', expand=True)

        self.salt_file = "salt.bin"
        self.salt = self.load_or_create_salt()

    def update_code_display(self, text):
        self.code_display.configure(text=text)

    def load_or_create_salt(self):
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as file:
                return file.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as file:
                file.write(salt)
            return salt

    def on_password_accepted(self, password):
        # Use the loaded or created salt
        self.encryption_handler = EncryptionHandler(password, self.salt)
        
        # Example usage: encrypting the password (replace this with your actual data encryption logic)
        encrypted_pass = self.encryption_handler.encrypt(password)
        self.accounts_frame = AccountsFrame(self, self.update_code_display, self.encryption_handler)
        print("Encrypted Password:", encrypted_pass)

        # Continue with showing the accounts frame
        self.password_frame.pack_forget()
        self.accounts_frame.pack(fill='both', expand=True)
        

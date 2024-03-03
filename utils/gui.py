import customtkinter as ct
from utils.tokens import OTPGenerator

class AccountsFrame(ct.CTkScrollableFrame):
    def __init__(self, master, update_label, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.update_label = update_label
        self.buttons = {}  # To keep track of buttons for deletion

        # Bind right-click context menu to frame
        self.bind("<Button-3>", self.show_context_menu)

        # Add New Token button inside the scrollable frame, makes it add a new button when clicked
        add_token_btn = ct.CTkButton(self, text='Add New Token', command=self.add_account)
        add_token_btn.pack(side='bottom', fill='x', padx=20, pady=10)

    def select_account(self, account_name):
        print(f'Account selected: {account_name}')

    def on_button_right_click(self, event, account_name):
        self.context_menu.tk_popup(event.x_root, event.y_root)
        self.account_to_delete = account_name  # Track which account to delete

    def delete_button(self):
        if self.account_to_delete in self.buttons:
            self.buttons[self.account_to_delete].destroy()  # Remove the button widget
            del self.buttons[self.account_to_delete]  # Remove the button from the dictionary

    def add_account(self):
        self.pack_forget()  # Hide the accounts frame
        self.update_label('Add Account')
        # Pass self.update_label to AddNewAccountFrame
        add_account_frame = AddNewAccountFrame(self.master, self.create_account_button, self.repack_accounts_frame, self.update_label)
        add_account_frame.pack(fill='both', expand=True)

    def repack_accounts_frame(self):
        self.pack(fill='both', expand=True)  # Repack the accounts frame with fill and expand


    def create_account_button(self, account_name):
        btn = ct.CTkButton(self, text=account_name, command=lambda: self.select_account(account_name))
        btn.pack(fill='x', padx=20, pady=10)
        btn.bind("<Button-3>", lambda event, acc=account_name: self.on_button_right_click(event, acc))
        self.buttons[account_name] = btn  # Store the new button

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

class AddNewAccountFrame(ct.CTkFrame):
    def __init__(self, master, on_accept, on_decline, update_label, **kwargs):
        super().__init__(master, **kwargs)
        self.on_accept = on_accept
        self.on_decline = on_decline
        self.update_label = update_label

        # Nickname Entry
        nickname_label = ct.CTkLabel(self, text="Nickname", font=("Roboto", 18))
        nickname_label.pack(pady=(10, 2))
        self.nickname_entry = ct.CTkEntry(self, placeholder_text="Nickname")
        self.nickname_entry.pack(pady=(2, 20))

        # Secret Entry
        secret_label = ct.CTkLabel(self, text="Secret", font=("Roboto", 18))
        secret_label.pack(pady=(10, 2))
        self.secret_entry = ct.CTkEntry(self, placeholder_text="Secret")
        self.secret_entry.pack(pady=(2, 90))

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
            # Check if the nickname already exists
            if nickname in self.master.accounts_frame.buttons:
                # Show an error message to the user
                error_label = ct.CTkLabel(self, text="Nickname already in use...", text_color='red')
                error_label.pack(pady=(10, 0))
            else:
                self.on_accept(nickname)
                self.pack_forget()  # Hide this frame
                otp = OTPGenerator(secret)  # Create an OTPGenerator instance
                self.update_label(otp.generate_otp())
                self.on_decline()  # Repack and show the accounts frame
        else:
            # Show an error message to the user
            error_label = ct.CTkLabel(self, text="Enter your info, my mans", text_color='red')
            error_label.pack(pady=(10, 0))

    def decline(self):
        self.pack_forget()  # Hide this frame
        self.update_label('Hello, world!')  # Reset the label when declining
        self.on_decline()  # Repack and show the accounts frame

class App(ct.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('350x610')
        ct.set_appearance_mode('dark')  # Set appearance mode
        ct.set_default_color_theme('dark-blue')  # Set color theme

        # Make code_display an instance variable by using self
        self.code_display = ct.CTkLabel(self, text='Hello, world!', font=('Roboto', 40))
        self.code_display.pack(pady=20, padx=20)

        self.accounts_frame = AccountsFrame(self, self.update_code_display)
        self.accounts_frame.pack(fill='both', expand=True)
    
    def update_code_display(self, text):
        # Now self.code_display is correctly referenced as an instance variable
        self.code_display.configure(text=text)
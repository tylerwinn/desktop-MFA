
from utils.tokens import TokenManager



def main():
    tm = TokenManager(password="test")
    account = tm.get_accounts()[0]
    token = tm.generate_token(account)
    print(f"Generated token for {account}: {token}")

if __name__ == "__main__":
    main()

import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, Property
from utils.tokens import TokenManager

class AccountListModel(QObject):
    tokenGenerated = Signal(str)  # Declare the signal

    def __init__(self):
        super().__init__()
        self._accounts = []
        self.tm = TokenManager(password="test")


    @Signal
    def accountsChanged(self):
        pass

    @Property(list, notify=accountsChanged)
    def accounts(self):
        return self._accounts

    @accounts.setter
    def accounts(self, val):
        if self._accounts == val:
            return
        self._accounts = val
        self.accountsChanged.emit()

    @Slot()
    def updateAccounts(self):
        accounts = self.tm.get_accounts()
        self.accounts = [{'name': account} for account in accounts]

    @Slot(str)
    def generateTokenForAccount(self, accountName):
        token = self.tm.generate_token(accountName)
        result = ' '.join([token[:3], token[3:]])
        self.tokenGenerated.emit(result)


def main():
    app = QGuiApplication(sys.argv)
    
    # Create the QML engine
    engine = QQmlApplicationEngine()
    
    # Create the account list model and set it as a context property
    accountListModel = AccountListModel()
    engine.rootContext().setContextProperty("accountListModel", accountListModel)

    # Load the QML file
    engine.load('app.qml')
    
    # Check if the engine loaded correctly
    if not engine.rootObjects():
        sys.exit(-1)

    # Update accounts once at startup
    accountListModel.updateAccounts()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

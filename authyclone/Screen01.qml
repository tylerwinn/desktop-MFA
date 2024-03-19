import QtQuick 6.5
import QtQuick.Controls 6.5

Rectangle {
    id: rectangle2
    width: 350
    height: 610
    color: "#000814"

    property int totalSeconds: 30
    property int remainingSeconds: 30 - Math.floor((new Date().getTime() / 1000) % 30)
    property string currentToken: qsTr("000 000") // Default token
    property string currentAccount: "" // Initialize to empty string

    function updateMfaCode(token) {
        currentToken = token;
        mfa_code.text = token;
    }

    Component.onCompleted: {
        accountListModel.tokenGenerated.connect(updateMfaCode);
        timer.restart();
    }

    Rectangle {
        id: rectangle
        x: 30
        y: 22
        width: 290
        height: 90
        color: "#003566"

        Timer {
            id: timer
            interval: 1000 // Update every second
            repeat: true
            running: true
            onTriggered: {
                remainingSeconds = 30 - Math.floor((new Date().getTime() / 1000) % 30);
                if (remainingSeconds === 30 && currentAccount) {
                    accountListModel.generateTokenForAccount(currentAccount);
                }
            }
        }

        Text {
            id: mfa_code
            x: 8
            y: 8
            width: 274
            height: 40
            color: "#ffffff"
            text: currentToken
            font.pixelSize: 48
            horizontalAlignment: Text.AlignHCenter
        }
        Rectangle {
            id: progressBar
            width: (rectangle.width) * ((totalSeconds - remainingSeconds) / totalSeconds)
            height: 5
            color: "#FFC300"
            x: 0
            y: rectangle.height - height // Positioned above the countdownText
        }
        Text {
            id: countdownText
            width: 274
            height: 20 
            x: rectangle.width - width - 8 
            y: rectangle.height - height - 8 
            color: "#ffffff"
            text: remainingSeconds + " sec(s)"
            font.pixelSize: 12
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignBottom
        }
    }

    Rectangle {
        id: rectangle1
        x: 30
        y: 144
        width: 290
        height: 442
        color: "#001D3D"
    }

    ListView {
        id: listView
        x: 45
        y: 155
        width: 260
        height: 420
        model: accountListModel.accounts
        property int selectedAccountIndex: -1

        delegate: Item {
            width: parent.width
            height: 40

            Rectangle {
                width: parent.width
                height: parent.height
                color: listView.selectedAccountIndex === index ? "#003566" : "transparent"

                Text {
                    width: parent.width
                    height: parent.height
                    text: modelData.name
                    font.pixelSize: 16
                    font.bold: true
                    color: "#ffffff"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    listView.selectedAccountIndex = index
                    currentAccount = modelData.name
                    accountListModel.generateTokenForAccount(modelData.name)
                    // Restart the timer each time a new account is clicked
                    timer.restart()
                }
            }
        }
    }
}

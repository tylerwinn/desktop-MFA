
import QtQuick 6.5
import QtQuick.Controls 6.5

Rectangle {
    id: rectangle2
    width: 350
    height: 610
    color: "#000814"

    // This function updates the MFA code text.
    function updateMfaCode(token) {
        mfa_code.text = token;
    }

    // When the component is completed, connect the signal to the update function.
    Component.onCompleted: {
        accountListModel.tokenGenerated.connect(updateMfaCode);
    }

    Rectangle {
        id: rectangle
        x: 30
        y: 22
        width: 290
        height: 90
        color: "#003566"

        Text {
            id: mfa_code
            x: 8
            y: 8
            width: 274
            height: 74
            color: "#ffffff"
            text: qsTr("000 000")
            font.pixelSize: 48
            horizontalAlignment: Text.AlignHCenter
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
        property int selectedAccountIndex: -1 // Renamed to avoid conflict

        delegate: Item {
            width: parent.width
            height: 40

            Rectangle {
                width: parent.width
                height: parent.height
                // Use the new property name here
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
                    listView.selectedAccountIndex = index // Update to use the new property name
                    accountListModel.generateTokenForAccount(modelData.name)
                }
            }
        }
    }
}

// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick 6.5

Window {
    width: mainScreen.width
    height: mainScreen.height

    visible: true
    maximumHeight: 610
    minimumHeight: 610
    minimumWidth: 350
    maximumWidth: 350
    title: "AuthyCloneGUI"

    Screen01 {
        id: mainScreen
    }

}


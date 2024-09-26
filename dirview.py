#!/usr/bin/python3


#############################################################################
##
## Copyright (C) 2017 Riverbank Computing Limited.
## Copyright (C) 2017 Hans-Peter Jansen <hpj@urpla.net>
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


import sys
import os

from PyQt5.QtCore import (QCommandLineOption, QCommandLineParser,
        QCoreApplication, QDir, QSortFilterProxyModel, QT_VERSION_STR,
        QModelIndex)
from PyQt5.QtWidgets import (QApplication, QFileIconProvider, QFileSystemModel,
        QTreeView, QLineEdit, QWidget, QLabel, QVBoxLayout)

def add_buttons():
    rootIndex = model.index(QDir.homePath())
    proxyRootIndex = proxyModel.mapFromSource(rootIndex)
    rowCount = model.rowCount(rootIndex)
    for row in range(rowCount):
        proxyNameIndex = proxyModel.index(row, 0, proxyRootIndex)
        sourceNameIndex = proxyModel.mapToSource(proxyNameIndex)
        sizeIndex = proxyModel.index(row, 1, proxyRootIndex)
        label = QLabel("Обновить")
        if model.isDir(sourceNameIndex):
            tree.setIndexWidget(sizeIndex, label)

def update_clicked(index: QModelIndex):
    sourceIndex = proxyModel.mapToSource(index)
    if model.data(sourceIndex) != '':
        return
    folderPath = model.filePath(sourceIndex)
    totalSize = 0
    for dirpath, dirnames, filenames in os.walk(folderPath):
        for filename in filenames:
            filePath = os.path.join(dirpath, filename)
            totalSize += os.path.getsize(filePath)
    label = QLabel(str(totalSize) + " байты")
    tree.setIndexWidget(index, label)

def update_filter(text):
    proxyModel.setFilterWildcard("*{}*".format(text))
    rootIndex = model.index(QDir.cleanPath(rootPath))
    proxyRootIndex = proxyModel.mapFromSource(rootIndex)
    tree.setRootIndex(proxyRootIndex)
    add_buttons()

app = QApplication(sys.argv)

QCoreApplication.setApplicationVersion(QT_VERSION_STR)
parser = QCommandLineParser()
parser.setApplicationDescription("Qt Dir View Example")
parser.addHelpOption()
parser.addVersionOption()

dontUseCustomDirectoryIconsOption = QCommandLineOption('c',
        "Set QFileIconProvider.DontUseCustomDirectoryIcons")
parser.addOption(dontUseCustomDirectoryIconsOption)
parser.addPositionalArgument('directory', "The directory to start in.")
parser.process(app)
try:
    rootPath = parser.positionalArguments().pop(0)
except IndexError:
    rootPath = QDir.homePath()

model = QFileSystemModel()
model.setRootPath(QDir.homePath())
model.setFilter(QDir.AllEntries | QDir.Hidden)
if parser.isSet(dontUseCustomDirectoryIconsOption):
    model.iconProvider().setOptions(
            QFileIconProvider.DontUseCustomDirectoryIcons)

proxyModel = QSortFilterProxyModel(recursiveFilteringEnabled=True, \
        filterRole=QFileSystemModel.FileNameRole)
proxyModel.setSourceModel(model)

tree = QTreeView()
tree.setModel(proxyModel)
if rootPath is not None:
    rootIndex = model.index(QDir.homePath())
    if rootIndex.isValid():
        proxyRootIndex = proxyModel.mapFromSource(rootIndex)
        tree.setRootIndex(proxyRootIndex)

# Demonstrating look and feel features.
tree.setAnimated(False)
tree.setIndentation(20)
tree.setSortingEnabled(True)


availableSize = QApplication.desktop().availableGeometry(tree).size()
tree.resize(availableSize / 2)
tree.setColumnWidth(0, int(tree.width() / 3))

tree.setWindowTitle("File View")

widget = QWidget()
layout = QVBoxLayout(widget)

line = QLineEdit()
line.setWindowTitle("Filter")

layout.addWidget(line)
layout.addWidget(tree)
widget.show()

tree.clicked.connect(lambda index: update_clicked(index))
model.directoryLoaded.connect(add_buttons)
line.textChanged.connect(update_filter)
tree.expanded.connect(add_buttons)

sys.exit(app.exec_())

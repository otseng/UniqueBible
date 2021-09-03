import os, config

from util.FileUtil import FileUtil

# Do not delete items from the following two lines.  It appears that some are not used but they are actually used somewhere else. 
from qtpy.QtGui import QIcon
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory, QComboBox
from functools import partial

def addMenu(menuBar, translation):
    return menuBar.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation[translation]))

def addSubMenu(parentMenu, translation):
    return parentMenu.addMenu(config.thisTranslation[translation])

def addMenuItem(menu, feature, object, action, shortcut=None, translation=True):
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    if shortcut is None:
        shortcut = ""
    return menu.addAction(QAction(config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addIconMenuItem(icon, menu, feature, object, action, shortcut=None, translation=True):
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    icon = QIcon(os.path.join("htmlResources", icon))
    return menu.addAction(QAction(icon, config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addMenuLayoutItems(parent, menu):
    items = (
        ("menu1_aleph_menu_layout", lambda: parent.setMenuLayout("aleph")),
        ("menu1_focus_menu_layout", lambda: parent.setMenuLayout("focus")),
        ("menu1_classic_menu_layout", lambda: parent.setMenuLayout("classic")),
    )
    for feature, action in items:
        addMenuItem(menu, feature, parent, action)
    layouts = FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "layout"), "py")
    if layouts:
        menu.addSeparator()
        for pluginLayout in layouts:
            addMenuItem(menu, pluginLayout, parent, lambda: parent.setMenuLayout(pluginLayout), translation=False)

def addGithubDownloadMenuItems(self, subMenu):
    if config.isPygithubInstalled:
        subMenu.addSeparator()
        items = (
            ("githubBibles", self.installGithubBibles),
            ("githubCommentaries", self.installGithubCommentaries),
            ("githubBooks", self.installGithubBooks),
            ("githubMaps", self.installGithubMaps),
            ("githubPdf", self.installGithubPdf),
            ("githubEpub", self.installGithubEpub),
            ("gitHubDevotionals", self.installGithubDevotionals),
            ("gitHubBibleMp3Files", self.installGithubBibleMp3),
            ("gitHubPluginsContext", self.installGithubPluginsContext),
            ("gitHubPluginsMenu", self.installGithubPluginsMenu),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)

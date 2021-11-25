# -*- coding: utf-8 -*-
# author:yangtao
# time: 2021/11/25


from PySide2 import QtWidgets


class FileDialog(QtWidgets.QFileDialog):
    """
    文件浏览器，可以同时选择文件和文件夹
    """
    def __init__(self, *args):
        super(FileDialog, self).__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        btns = self.findChildren(QtWidgets.QPushButton)
        self.open_btn = [btn for btn in btns if u'open' in str(btn.text()).lower()][0]
        self.open_btn.clicked.disconnect()
        self.open_btn.clicked.connect(self.__open_clicked)
        self.tree = self.findChild(QtWidgets.QTreeView)

        self.files = []

    def __open_clicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        self.files = []
        for i in inds:
            if i.column() == 0:
                self.files.append(str(self.directory().absolutePath()).replace(u"\\", u"/") +
                                  u"/" +
                                  str(i.data()).replace(u"\\", u"/"))
        self.hide()

    @classmethod
    def get_files_and_dirs(cls, *args):
        dialog = cls(*args)
        dialog.setFileMode(dialog.ExistingFiles)
        dialog.exec_()
        return dialog.files

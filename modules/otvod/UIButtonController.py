class ButtonController:

    def __init__(self, buttons):
        super().__init__()
        self.buttons = buttons

    def lockAllButtons(self):
        for btn in self.buttons:
            for btn in self.buttons:
                btn.setEnabled(False)

    def unlockAllButtons(self):
        for btn in self.buttons:
            btn.setEnabled(True)

    def lockLesosekaButtons(self):
        for btn in self.buttons[1:]:
            btn.setEnabled(False)

    def unlockBuildButton(self):
        self.buttons[0].setEnabled(True)

    def unlockSaveDeleteButtons(self):
        self.buttons[2].setEnabled(True)
        self.buttons[1].setEnabled(True)
        self.buttons[3].setEnabled(True)

    def unlockReportBotton(self):
        self.buttons[4].setEnabled(True)

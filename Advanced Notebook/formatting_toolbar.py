



class FormattingToolbar(QToolBar):
    def __init__(self, editor: QTextEdit, parent=None):
        """
        Bold action
        Italic action
        Underline action
        Strikeout action
        Font family selector
        Font-size selector
        Text-color button
        Highlight-color button
        Left-align action
        Center-align action
        Right-align action
        Justify action
        Bulleted-list action
        Numbered-list action

        Args:
            editor (QTextEdit): _description_
            parent (_type_, optional): _description_. Defaults to None.
        """

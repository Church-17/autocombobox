import sys
from tkinter import Tk, StringVar
from tkinter.ttk import Combobox, Label, Style
sys.path.append('.')
from src.autocombobox import AutoCombobox

values = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink", "Grey", "White", "Black", "Brown"]
# values = values[0:2]

class Main:
    def __init__(self):
        self.count = 0
        self.root = Tk()
        self.root.title("Test")
        # self.root.geometry("300x300")
        self.root.rowconfigure((1, 2), weight=1)
        self.root.columnconfigure((0, 1), weight=1)

        self.stringvar1 = StringVar(self.root)
        self.stringvar2 = StringVar(self.root)
        self.kwargs = {
            "values": values,
            "justify": "center",
            "height": 5,
            'width': 30,
        }
        # Create a style
        style = Style(self.root)

        # Set the theme with the theme_use method
        # style.theme_use('clam')  # put the theme name here, that you want to use

        Label(self.root, text="Normal combobox").grid(row=0, column=0, sticky="n")
        self.combo = Combobox(self.root, **self.kwargs, postcommand=self.postcmd, textvariable=self.stringvar1)
        self.combo.grid(row=1, column=0, sticky="n")
        self.combo.bind("<<ComboboxSelected>>", self.selected)

        Label(self.root, text="AutoCombobox").grid(row=0, column=1, sticky="n")
        self.autocombo = AutoCombobox(self.root, **self.kwargs, textvariable=self.stringvar2)
        self.autocombo['postcommand']=self.postcmd
        self.autocombo.grid(row=1, column=1, sticky="n")
        self.autocombo.bind("<<ComboboxSelected>>", self.selected)

        self.news = Label(self.root)
        self.news.grid(row=2, column=0, columnspan=2, sticky="s")

        self.root.mainloop()

    def selected(self, event):
        if event.widget == self.combo:
            self.news.config(text=f"Selected {self.stringvar1.get()}")
        elif event.widget == self.autocombo:
            self.news.config(text=f"Selected {self.stringvar2.get()}")

    def postcmd(self):
        self.news.config(text=f"Postcommand {self.count}")
        self.count += 1

if __name__ == "__main__":
    Main()

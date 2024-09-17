# AutoCombobox

[![PyPI](https://img.shields.io/pypi/v/autocombobox?style=flat)](https://pypi.python.org/pypi/autocombobox/)

AutoCombobox is a Ttk widget based on the existing Combobox. It allows the user to write on the entry field, viewing at the same time some suggested option based on what the user writes. The suggestions are customizable through a function that can be defined by the developer.

## Installation

AutoCombobox can be installed from PyPI using the command `pip install autocombobox`.
It doesn't have any dependences other than Tkinter.

## Usage

AutoCombobox was created specifically to be used like the normal Ttk Combobox, so all its options are available.
Beside that, it can accept the `filter` option, that allows the developer to pass the function that determines the suggestions. The function must take 2 parameters: the first represent the list of all possible options of the Combobox, and the second represent the text written on the entry field; the function must returns a list of integers rappresenting the indices of the position of each option (a negative value indicates that the option will not be shown). There is a default filter function, that shows all the options that starts with the user input.

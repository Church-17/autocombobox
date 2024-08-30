# AutoCombobox

AutoCombobox is a ttk widget based on the existing Combobox. It allows the user to write on the Entry field, viewing at the same time the options that the Combobox suggest based on what the user writes.

## Installation

AutoCombobox can be installed from PyPI: `pip install autocombobox`.

It doesn't have any dependences other than tkinter.

## Usage

AutoCombobox was created specifically to be used like the normal ttk Combobox, so all its options are available.
Beside that, it can accept the `filter` option, that allows the developer to pass the function that determines the suggestions. The function must take 2 parameters: the first represent the text written on the Entry, and the second represent a possible value of the Combobox; the function then must returns a boolean value, which indicates whetever the option passed as the second parameter will be included in the suggestions or not.

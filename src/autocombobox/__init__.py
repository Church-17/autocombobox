from collections.abc import Callable
from tkinter import Listbox, Event, Frame
from tkinter.ttk import Combobox, Scrollbar

__version__ = "1.0.2"

class AutoCombobox(Combobox):
    """Autocomplete Combobox"""

    def __init__(self, *args, **kwargs):
        """Create an Autocomplete ttk Combobox. All the ttk Combobox options are available.
        
        Use simil_func to pass the function for filtering the suggestions"""

        # Declare helper variables
        self._is_posted: bool = False
        self._changed_listbox: bool = False
        self._highlighted_index: int = -1
        self._selected_str: str | None = None
        self._old_postcommand: Callable[[], object] | None = None

        # Create Combobox object
        super().__init__(*args, postcommand=self._postcommand)
        if "simil_func" not in kwargs:
            kwargs["simil_func"] = None
        self.configure(**kwargs)

        # Declare dependent variables
        toplevel = self.winfo_toplevel()
        self._listbox_values: tuple[str] = self["values"]

        # Create & configure listbox frane
        self._frame = Frame(toplevel, background="white", highlightbackground="grey48", highlightthickness=1)
        self._listbox = Listbox(self._frame, activestyle="none", width=self["width"], borderwidth=0, highlightthickness=0)
        self._scrollbar = Scrollbar(self._frame, command=self._listbox.yview)
        self._listbox.grid(row=0, column=0, padx=(1, 3), pady=1)
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._listbox.config(yscrollcommand = self._scrollbar.set)

        # Bind events
        toplevel.bind("<Button-1>", self._click_event)      # Handle mouse click
        toplevel.bind("<Configure>", self._window_event)    # Handle window events
        self.bind("<KeyRelease>", self._type_event)         # Handle keyboard typing to display coherent options
        self.unbind_class("TCombobox", "<Down>")            # Handle keyboard typing to display coherent options
        self._listbox.bind("<Motion>", self._motion_event)  # Handle mouse movement to control highlight
        self._listbox.bind("<Leave>", self._leave_event)    # Handle mouse movement to control highlight

    def show_listbox(self):
        """Open the Combobox popdown"""

        # Execute user postcommand if there is one
        if self._old_postcommand:
            self._old_postcommand()

        # Show frame & update vars
        toplevel = self.winfo_toplevel()
        self._frame.place(x=self.winfo_rootx()-toplevel.winfo_rootx(), y=self.winfo_rooty()-toplevel.winfo_rooty()+self.winfo_height())
        self._frame.lift()
        self._is_posted = True

        # If the current text is an option, reset listbox & select text
        if self._selected_str != None and self.get().lower() == self._selected_str.lower():
            self.update_values("")
            self.select_range(0, "end")
            self.icursor("end")
        else:
            self.update_values()

        # If the selected option is in listbox, view it
        if self._selected_str in self._listbox_values:
            self._listbox.see(self._listbox_values.index(self._selected_str))

    def hide_listbox(self):
        """Hide the Combobox popdown"""

        # Hide frame
        self._frame.place_forget()
        self.change_highlight(-1)
        self._is_posted = False

    def update_values(self, text: str | None = None):
        """Update listbox values to show coherent options"""

        # Check params
        if text == None:
            text = self.get()
        elif type(text) != str:
            text = str(text)

        # Change listbox values
        self._listbox_values = [opt for opt in self["values"] if self._simil_func(text, opt)]
        self._listbox.delete(0, "end")
        self._listbox.insert(0, *self._listbox_values)

        # Adapt listbox geight and don't show scrollbar if it isn't needed
        if self._listbox.size() <= int(self["height"]):
            height = self._listbox.size()
            self._scrollbar.grid_forget()
        else:
            height = self["height"]
            self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._listbox.config(height=height)
        self._changed_listbox = True

        # Highlight selected option if it is in listbox
        if self._selected_str in self._listbox_values:
            self.change_highlight(self._listbox_values.index(self._selected_str))
        elif self._listbox_values:
            self.change_highlight(0)

    def select(self, option: str):
        """Select one of the possible options"""

        # Check params
        if type(option) != str:
            option = str(option)

        # Set Combobox on the given value
        self.set(option)
        self.icursor("end")
        self.hide_listbox()
        self.focus()
        if option in self["values"]:
            self._selected_str = option
            self.select_range(0, "end")
            self.event_generate("<<ComboboxSelected>>")

    def change_highlight(self, index: int):
        """Highlight the option corresponding to the given index and remove highlight from the old one"""

        # Check params
        if type(index) != int:
            index = int(index)

        # Remove highlight
        if self._highlighted_index >= 0 and self._highlighted_index < self._listbox.size():
            self._listbox.itemconfig(self._highlighted_index, {"bg": "white"})
            self._listbox.itemconfig(self._highlighted_index, {"fg": "black"})

        # Highlight
        if index >= 0 and index < self._listbox.size():
            self._listbox.itemconfig(index, {"bg": "#0078d7"})
            self._listbox.itemconfig(index, {"fg": "white"})
            self._highlighted_index = index
            self._listbox.see(index)
        else:
            self._highlighted_index = -1

    def _click_event(self, event: Event):
        """Handle mouse click"""

        # Hide listbox if clicked outside
        if self._is_posted and event.widget != self and event.widget != self._listbox and event.widget != self._scrollbar and event.widget != self._frame:
            self.hide_listbox()

        elif event.widget == self:
            # If listbox is open, update it
            if self._is_posted:
                self.update_values()

            # If listbox is not opened, open it
            else:
                self.show_listbox()

        # If clicked on listobox select the option
        elif event.widget == self._listbox and self._highlighted_index >= 0:
            self.select(self._listbox_values[self._highlighted_index])

    def _window_event(self, event: Event):
        """Handle window events"""

        # Hide listbox if user interact with the window
        if self._is_posted and event.widget == self.winfo_toplevel():
            self.hide_listbox()

    def _type_event(self, event: Event):
        """Handle keyboard typing"""

        if self._is_posted:
            # Gide listbox when ESC pressed
            if event.keysym == "Escape":
                self.hide_listbox()

            # Select the highlighted option if is pressed enter
            elif event.keysym == "Return" and self._highlighted_index >= 0:
                self.select(self._listbox_values[self._highlighted_index])

            # If arrow pressed, move highlight
            elif event.keysym == "Down":
                if self._highlighted_index + 1 < self._listbox.size():
                    self.change_highlight(self._highlighted_index + 1)
            elif event.keysym == "Up":
                if self._highlighted_index - 1 >= 0:
                    self.change_highlight(self._highlighted_index - 1)

            # If home pressed, highlight first option
            elif event.keysym == "Home":
                self.change_highlight(0)

            # If end pressed, highlight last option
            elif event.keysym == "End":
                self.change_highlight(self._listbox.size()-1)
            
            # Filter options
            else:
                self.update_values()

        # Show listbox if is not opened
        elif event.char != "" or event.keysym == "Down" or event.keysym == "BackSpace" or event.keysym == "Return":
            self.show_listbox()

    def _motion_event(self, event: Event):
        """Handle mouse movement"""

        # Restore vars
        self._changed_listbox = False

        # Highlight option under mouse and remove highlight from the old one
        index = self._listbox.index(f"@{event.x},{event.y}")
        if self._highlighted_index != index:
            self.change_highlight(index)

    def _leave_event(self, event: Event):
        """Handel mouse leaving listbox"""

        # Remove highlight if listbox is not changed
        if not self._changed_listbox:
            self.change_highlight(-1)

    # Override configure method to always handle options
    def configure(self, *args, **kwargs):

        # Override postcommand parameter
        if "postcommand" in kwargs:
            self._old_postcommand = kwargs["postcommand"]
            kwargs.pop("postcommand")

        # Handle simil_func parameter
        if "simil_func" in kwargs:
            if kwargs["simil_func"]:
                self._simil_func = kwargs["simil_func"]
            else:
                self._simil_func = lambda text, opt: text.lower() in opt.lower()
            kwargs.pop("simil_func")

        return super().configure(*args, **kwargs)

    config = configure

    def _postcommand(self):
        """Define new postcommand function to show only the new listbox and not the internal one"""

        # If the listbox is opened, hide it
        if self._is_posted:
            self.after(0, self.hide_listbox)

        # Hide internal listbox
        self.after(0, lambda: self.tk.call("ttk::combobox::Unpost", self))

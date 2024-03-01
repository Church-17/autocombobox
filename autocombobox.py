from tkinter import Listbox, Event, Frame
from tkinter.ttk import Combobox, Scrollbar

class AutoCombobox(Combobox):
    """Autocomplete Combobox"""

    def __init__(self, *args, **kwargs):
        """Create an Autocomplete ttk Combobox. Options are the same of ttk Combobox"""

        # Declare helper variables
        self._is_posted: bool = False
        self._is_select_restored: bool = True
        self._highlighted_index: int = -1
        self._selected_str: str = ""

        # Create Combobox object
        super().__init__(*args)
        self.configure(**kwargs)
        self.config = self.configure

        # Declare dependent variables
        toplevel = self.winfo_toplevel()
        self._listbox_values: tuple = self["values"]

        # Create & configure listbox frane
        self._frame = Frame(toplevel, background="white", highlightbackground="grey48", highlightthickness=1)
        self._listbox = Listbox(self._frame, activestyle="none", width=self["width"], borderwidth=0, highlightthickness=0)
        self._scrollbar = Scrollbar(self._frame, command=self._listbox.yview)
        self._listbox.grid(row=0, column=0, padx=(1, 3), pady=1)
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self.update_values("")
        self._listbox.config(yscrollcommand = self._scrollbar.set)

        # Bind events
        toplevel.bind("<Button-1>", self._click_event)      # Handle mouse click
        toplevel.bind("<Configure>", self._window_event)    # Handle window events
        self.bind("<KeyRelease>", self._type_event)         # Handle keyboard typing to display coherent options
        self.unbind_class("TCombobox", "<Down>")            # Handle keyboard typing to display coherent options
        self._listbox.bind("<Motion>", self._motion_event)  # Handle mouse movement to control highlight
        self._listbox.bind("<Leave>", self._leave_event)    # Handle mouse movement to control highlight

    # Override configure method to always handle options
    def configure(self, *args, **kwargs):
        if "postcommand" in kwargs:
            self._old_postcommand = kwargs["postcommand"]
        else:
            self._old_postcommand = None
        kwargs["postcommand"] = self._postcommand
        return super().configure(*args, **kwargs)

    def show_listbox(self):
        """Open the Combobox popdown"""
        self._is_posted = True
        toplevel = self.winfo_toplevel()
        self._frame.place(x=self.winfo_rootx()-toplevel.winfo_rootx(), y=self.winfo_rooty()-toplevel.winfo_rooty()+self.winfo_height())
        self._frame.lift()

        # If the current text is an option, reset listbox & select text
        if self.get().lower() in list(map(lambda s: s.lower(), self["values"])):
            self.update_values("")
            self.select_range(0, "end")
        else:
            self.update_values()
            
        # If the selected option is in listbox, view it
        if self._selected_str in self._listbox_values:
            self._listbox.see(self._listbox_values.index(self._selected_str))

    def hide_listbox(self):
        """Hide the Combobox popdown"""
        self._is_posted = False
        self._highlighted_index = -1
        self._frame.place_forget()

    def update_values(self, text: str | None = None):
        """Update listbox values to show coherent options"""
        if text == None:
            text = self.get()
        if type(text) != str:
            raise TypeError("Parameter 'text' must be of types 'str' or 'None'")

        # Change listbox values
        self._listbox_values = [opt for opt in self["values"] if text.lower() in opt.lower()]
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

        # Highlight selected option if it is in listbox
        if self._selected_str in self._listbox_values:
            self._is_select_restored = False
            self.highlight(self._listbox_values.index(self._selected_str))
        elif self._listbox_values:
            self.highlight(0)

    def select(self, option: str | int):
        """Select a value"""

        # Check option validity
        if type(option) == int:
            if option >= 0 and option < len(self["values"]):
                self._selected_str = self._listbox_values[option]
            else:
                raise ValueError("Given index out of values bound")
        elif type(option) == str:
            if option not in self["values"]:
                raise ValueError("Given option not in values")
            else:
                self._selected_str = option
        else:
            raise TypeError("Parameter 'option' must be of types 'str', 'int' or 'None'")

        # If something is highlighted, set Combobox on that value
        self.set(self._selected_str)
        self.select_range("end", "end")
        self.icursor("end")
        self.hide_listbox()
        self.event_generate("<<ComboboxSelected>>")

    def highlight(self, index: int):
        """Highlight the option corresponding to the given index"""
        if type(index) != int or index < 0 or index > self._listbox.size():
            raise TypeError("Given index must referes to a listbox item")

        self._highlighted_index = index
        self._listbox.itemconfig(index, {"bg": "#0078d7"})
        self._listbox.itemconfig(index, {"fg": "white"})

    def unhighlight(self, index):
        """Remove highlight from the option corresponding to the given index"""
        if type(index) != int or index < 0 or index > self._listbox.size():
            raise TypeError("Given index must referes to a listbox item")

        self._highlighted_index = -1
        self._listbox.itemconfig(index, {"bg": "white"})
        self._listbox.itemconfig(index, {"fg": "black"})

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
            self.select(self._highlighted_index)

    def _window_event(self, event: Event):
        """Handle window events"""
        if self._is_posted and event.widget == self.winfo_toplevel():
            self.hide_listbox()

    def _type_event(self, event: Event):
        """Handle keyboard typing"""

        if self._is_posted:
            # Gide listbox when ESC pressed
            if event.keysym == "Escape":
                self.hide_listbox()
                return

            # Select the highlighted option if is pressed enter
            if event.keysym == "Return" and self._highlighted_index >= 0:
                self.select(self._highlighted_index)
                return

            # If arrow pressed, move highlight
            if event.keysym == "Down" or event.keysym == "Up":
                # Determine direction
                if event.keysym == "Down":
                    direction = 1
                elif event.keysym == "Up":
                    direction = -1
                
                # Update highlight & see it
                new_highlight = self._highlighted_index + direction
                if new_highlight >= 0 and new_highlight < self._listbox.size():
                    if self._highlighted_index >= 0:
                        self.unhighlight(self._highlighted_index)
                    self.highlight(new_highlight)
                    self._listbox.see(self._highlighted_index)
                
                # Block internal bind
                return "break"
        
        # Show listbox if is not opened
        elif event.char != "" or event.keysym == "Down" or event.keysym == "BackSpace" or event.keysym == "Return":
            self.show_listbox()
            if event.keysym == "Down" or event.keysym == "Return":
                return

        # Show coherent value
        self.update_values()

    def _motion_event(self, event: Event):
        """Handel mouse movement"""
        # Restore highlight of _selected_str option if needed    
        if not self._is_select_restored:
            self._is_select_restored = True
            if self._selected_str in self._listbox_values:
                self.unhighlight(self._listbox_values.index(self._selected_str))

        # Highlight option under mouse and remove highlight from the old one
        index = self._listbox.index(f"@{event.x},{event.y}")
        if self._highlighted_index != index:
            if self._highlighted_index >= 0 and self._highlighted_index < self._listbox.size():
                self.unhighlight(self._highlighted_index)
            if index >= 0:
                self.highlight(index)

    def _leave_event(self, event: Event):
        """Handel mouse leaving listbox"""
        if self._highlighted_index >= 0 and self._highlighted_index < self._listbox.size():
            self.unhighlight(self._highlighted_index)

    def _postcommand(self):
        """Define new postcommand function to show only the new listbox and not the internal one"""
        # Execute user postcommand if there is one
        if self._old_postcommand:
            self._old_postcommand()
        
        # If the listbox is opened, hide it
        if self._is_posted:
            self.after(0, self.hide_listbox)

        # Hide internal listbox
        self.after(0, lambda: self.tk.call("ttk::combobox::Unpost", self))

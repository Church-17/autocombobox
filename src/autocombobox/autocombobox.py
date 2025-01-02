from collections.abc import Callable
import tkinter as tk
import tkinter.ttk as ttk

from .filters import default_filter


class AutoCombobox(ttk.Combobox):
    """Autocompleting Combobox"""

    def __init__(self,
            master = None,
            filter: Callable[[tuple[str], str], list[int]] = default_filter,
            **kwargs
        ) -> None:
        """
        Create an Autocompleting Ttk Combobox. All the Ttk Combobox options are available.
        
        Use the parameter `filter` to pass the function for filtering the suggestions.
        It must be a callable object that takes in this order the list of options and what the user writes,
        and returns a list of integers indicates the position of each option, using a negative value to not show it.
        
        The default filter function shows all the options that starts with the user input
        """

        # Interval variables
        self._is_posted: bool = False
        self._postcommand_done: bool = False
        self._prevent_leave: bool = False
        self._highlighted_index: int = -1
        self._selected_str: str | None = None
        self['postcommand'] = None
        self['filter'] = filter
        self._listbox_values: list[str] = []

        # Create Combobox
        super().__init__(master, postcommand=self._postcommand)
        self.configure(**kwargs)

        # Listbox toplevel
        self._toplevel = tk.Toplevel(self)
        self._toplevel.overrideredirect(True)
        self._toplevel.columnconfigure(0, weight=1)
        self._toplevel.rowconfigure(0, weight=1)
        self._frame = ttk.Frame(self._toplevel, style="ComboboxPopdownFrame")
        self._frame.grid(column=0, row=0, sticky="NSEW")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self._listbox = tk.Listbox(self._frame,
            activestyle="none",
            selectmode="browse",
            exportselection=False,
            **{k: self._retrieve_listbox_attr(k) for k in {"background", "bd", "bg", "border", "borderwidth", "cursor", "disabledforeground", "fg", "font", "foreground", "highlightbackground", "highlightcolor", "highlightthickness", "justify", "relief", "selectbackground", "selectborderwidth", "selectforeground"}}
        )
        self._scrollbar = ttk.Scrollbar(self._frame, command=self._listbox.yview)
        self._listbox.configure(yscrollcommand = self._scrollbar.set)

        # Events
        # - Unbind keyboard down to not post original listbox
        self.tk.eval(f"bind {self} <Down> break")
        # - Handle mouse click
        self.bind_all("<Button-1>", self._click_event)
        # - Handle keyboard typing to display coherent options
        self.bind("<KeyRelease>", self._type_event)
        self._toplevel.bind("<KeyRelease>", self._type_event)
        # - Handle window events
        self.winfo_toplevel().bind("<Configure>", self._window_event)
        # Handle mouse movement to control highlight
        self._listbox.bind("<Motion>", self._motion_event)
        self._listbox.bind("<Leave>", self._leave_event)

    def show_listbox(self) -> None:
        """Open the Combobox popdown"""

        # Execute user postcommand if there is one
        if self._user_postcommand:
            self._user_postcommand()

        # Show listbox toplevel
        self._toplevel.manage(self._toplevel)
        self._toplevel.lift()
        
        # If the current text is an option, reset listbox
        if self.get() == self._selected_str:
            self.update_values("")

        # If listbox empty, reset listbox & select text
        elif len(self._listbox_values) == 0:
            self.update_values("")
            self.selection_range(0, "end")
            self.icursor("end")
        
        # Else update listbox
        else:
            self.update_values()

        # If the selected option is in listbox, view it
        if self._selected_str in self._listbox_values:
            self._listbox.see(self._listbox_values.index(self._selected_str))

        self._is_posted = True

    def hide_listbox(self) -> None:
        """Hide the Combobox popdown"""

        # Reset highglight
        self.change_highlight(-1)

        # Hide listbox toplevel
        self._toplevel.forget(self._toplevel)
        self._is_posted = False

    def update_values(self, text: str | None = None) -> None:
        """Update listbox values to show coherent options"""

        # Check params
        if text == None:
            text = self.get()
        elif not isinstance(text, str):
            text = str(text)

        # Change listbox values
        indices = self._filter(self["values"], text)
        assert len(indices) == len(self["values"]), "The length of the list returned by the filter function does not match the length of the values"
        self._listbox_values = [opt for i, opt in sorted(zip(indices, self["values"])) if i >= 0]
        self._listbox.delete(0, "end")
        self._listbox.insert(0, *self._listbox_values)

        # Adapt listbox height and don't show scrollbar if it isn't needed
        if self._listbox.size() <= int(self["height"]):
            self._listbox.configure(height=self._listbox.size())
            self._scrollbar.grid_forget()
            self._listbox.grid(row=0, column=0, padx=1, pady=1, sticky="NSEW")
        else:
            self._listbox.configure(height=self["height"])
            self._scrollbar.grid(row=0, column=1, padx=(0,1), pady=1, sticky="NS")
            self._listbox.grid(row=0, column=0, padx=(1,0), pady=1, sticky="NSEW")
        self._frame.update_idletasks()
        self._toplevel.geometry(f"{self.winfo_width()}x{self._frame.winfo_reqheight()}+{self.winfo_rootx()}+{self.winfo_rooty()+self.winfo_height()}")

        # Highlight selected option if it is in listbox
        if self._selected_str in self._listbox_values:
            self.change_highlight(self._listbox_values.index(self._selected_str))
        elif self._listbox_values:
            self.change_highlight(0)

    def select(self, option: str) -> None:
        """Select one of the possible options"""

        # Check params
        if not isinstance(option, str):
            option = str(option)

        # Focus on Combobox
        self.hide_listbox()
        self.focus()

        # Set Combobox on the given value
        self.set(option)
        self.icursor("end")
        if option in self["values"]:
            self._selected_str = option
            self.selection_range(0, "end")
            self.event_generate("<<ComboboxSelected>>")

    def change_highlight(self, index: int) -> None:
        """Highlight the option corresponding to the given index and remove highlight from the old one"""

        # Check params
        if not isinstance(index, int):
            index = int(index)

        # Remove previous highlight
        self._listbox.selection_clear(0, "end")

        # Add new highlight if valid index
        if 0 <= index < self._listbox.size():
            self._listbox.selection_set(index)
            self._listbox.see(index)
            self._highlighted_index = index
        else:
            self._highlighted_index = -1

    def _click_event(self, event: tk.Event) -> None:
        """Handle mouse click"""

        # Handle str event widget
        if not isinstance(event.widget, tk.Misc):
            self.hide_listbox()
        
        elif event.widget == self:
            # If it's done also the postcommand, do nothing and reset vars
            if self._postcommand_done:
                self._postcommand_done = False
            else:
                # If click on Combobox and the listbox is already shown, update listbox
                if self._is_posted:
                    self.update_values()
                # If click on Combobox and the listbox isn't shown, show it
                else:
                    self.show_listbox()

        elif self._is_posted:
            # If click outside and the listbox is shown, hide it
            if event.widget.winfo_toplevel() != self._toplevel:
                self.hide_listbox()

            # If click in listbox, select the highlighted value
            elif event.widget == self._listbox and self._highlighted_index >= 0:
                self.select(self._listbox_values[self._highlighted_index])

    def _window_event(self, event: tk.Event) -> None:
        """Handle window events"""

        # Hide listbox if user interact with the window
        if self._is_posted and event.widget == self.winfo_toplevel():
            self.hide_listbox()

    def _type_event(self, event: tk.Event) -> None:
        """Handle keyboard typing"""

        if self._is_posted:
            # Hide listbox when ESC pressed
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
                self._prevent_leave = True

        # Show listbox if is not opened
        elif event.char != "" or event.keysym == "Down" or event.keysym == "BackSpace" or event.keysym == "Return":
            self.show_listbox()

    def _motion_event(self, event: tk.Event) -> None:
        """Handle mouse movement"""

        # Highlight option under mouse and remove highlight from the old one
        index = self._listbox.index(f"@{event.x},{event.y}")
        if self._highlighted_index != index:
            self.change_highlight(index)

    def _leave_event(self, event: tk.Event) -> None:
        """Handle mouse leaving listbox"""

        # Remove highlight when leave moving cursor
        if self._prevent_leave:
            self._prevent_leave = False
        else:
            self.change_highlight(-1)

    def _postcommand(self) -> None:
        """Define new postcommand function to show only the new listbox and not the internal one"""

        # Show or hide listbox
        if self._is_posted:
            self.hide_listbox()
        else:
            self.show_listbox()
        self._postcommand_done = True

        # Hide internal listbox
        self.after(0, lambda: self.tk.call("ttk::combobox::Unpost", self))

    def _retrieve_listbox_attr(self, attr: str) -> str:
        """Function to retrieve attributes of Combobox Listbox"""

        return self.tk.eval(f'[ttk::combobox::PopdownWindow {self}].f.l cget -{attr}')

    # Methods to override to always handle parameters

    def configure(self, cnf = None, **kwargs):

        for param in {"postcommand", "filter"}:
            self[param] = kwargs.pop(param, self[param])

        return super().configure(cnf, **kwargs)

    config = configure

    def __getitem__(self, key) -> object:
        if key == "postcommand":
            return self._user_postcommand
        elif key == "filter":
            return self._filter
        else:
            return super().__getitem__(key)

    def __setitem__(self, key, value) -> None:
        if key == "postcommand":
            self._user_postcommand: Callable[[], object] | None = value
        elif key == "filter":
            self._filter: Callable[[tuple[str], str], list[int]] = value
        else:
            super().__setitem__(key, value)

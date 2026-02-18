# Grouping  Checkboxes for Better Layout

# Reorganized the checkboxes into three visual sections:

# Character Conversions - Digits, Words, Whitespace
# Pattern Matching - Repetitions, Capturing Groups, Verbose Mode, Case Insensitive
# Anchors - Start Anchor, End Anchor


import tkinter as tk
from tkinter import ttk, scrolledtext

from regex_builder import RegExpBuilder, generate_candidates, safe_match, analyze_regex_for_backtracking
from trie import Trie

import re
from regex_builder import RegExpConfig


class Tooltip:
    # Simple tooltip helper for tkinter widgets
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip = None

    def show(self, event=None):
        # update status bar (if available) and show popup
        try:
            set_status(self.text)
        except Exception:
            pass
            
        if self.tip:
            return

        x = y = 0
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tip, text=self.text, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack()
        
    def hide(self, event=None):
        # clear status bar and hide popup
        try:
            set_status("")
        except Exception:
            pass

        if self.tip:
            self.tip.destroy()
            self.tip = None

def set_status(text: str):
    """Set the status bar text if the status widget exists."""
    try:
        status_var.set(text)
    except Exception:
        pass

def generate_button_action():
    input_text = input_box.get("1.0", tk.END).strip().splitlines()
    builder = RegExpBuilder.from_test_cases(input_text)

    if digits_var.get():
        builder.with_conversion_of_digits()
    if words_var.get():
        builder.with_conversion_of_words()
    if whitespace_var.get():
        builder.with_conversion_of_whitespace()
    if repetitions_var.get():
        builder.with_conversion_of_repetitions()
    if capturing_var.get():
        builder.with_capturing_groups()
    if verbose_var.get():
        builder.with_verbose_mode()
    if case_var.get():
        builder.with_case_insensitive()
    if not start_anchor_var.get():
        builder.without_start_anchor()
    if not end_anchor_var.get():
        builder.without_end_anchor()

    '''
    regex = builder.build()
    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, regex)
    output_box.config(state='disabled')
    '''

    # Get candidate regexes from all generalization modes
    global current_candidates
    current_candidates = []
    seen_patterns = set()
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        builder.with_generalization(mode)
        candidates = builder.get_candidates(max_candidates=100)  # Get all candidates
        
        for c in candidates:
            pattern = c['pattern']
            # Deduplicate by pattern
            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                current_candidates.append(c)
                
    # Populate the candidates table
    candidates_tree.delete(*candidates_tree.get_children())

    for i, c in enumerate(current_candidates):
        summary = (c['pattern'][:60] + '...') if len(c['pattern']) > 60 else c['pattern']
        warn = '⚠' if c.get('warning') else ''
        tags = ('warn',) if c.get('warning') else ()
        candidates_tree.insert('', 'end', iid=str(i), values=(i+1, summary, c['reason'], warn), tags=tags)

    # Auto-select first candidate and show details
    if current_candidates:
        candidates_tree.selection_set('0')
        candidates_tree.focus('0')
        show_candidate_details()

root = tk.Tk()
root.title("Safe PyRex GUI")

input_box = tk.Text(root, height=10, width=50)
input_box.pack()

options_frame = tk.Frame(root)
options_frame.pack()

digits_var = tk.BooleanVar()
words_var = tk.BooleanVar()
whitespace_var = tk.BooleanVar()
repetitions_var = tk.BooleanVar()
capturing_var = tk.BooleanVar()
verbose_var = tk.BooleanVar()
case_var = tk.BooleanVar()
start_anchor_var = tk.BooleanVar(value=True)
end_anchor_var = tk.BooleanVar(value=True)

options = [
    ("Digits \\d", digits_var),
    ("Words \\w", words_var),
    ("Whitespace \\s", whitespace_var),
    ("Repetitions", repetitions_var),
    ("Capturing Groups", capturing_var),
    ("Verbose Mode", verbose_var),
    ("Case Insensitive", case_var),
    ("Start Anchor ^", start_anchor_var),
    ("End Anchor $", end_anchor_var),
]

for text, var in options:
    ttk.Checkbutton(options_frame, text=text, variable=var).pack(side=tk.LEFT)

ttk.Button(root, text="Generate Regex", command=generate_button_action).pack()

output_box = tk.Text(root, height=5, width=50, state='disabled')
output_box.pack()

root.mainloop()

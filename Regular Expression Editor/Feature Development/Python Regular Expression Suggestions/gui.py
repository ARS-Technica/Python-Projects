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
        warn = '⚠' if c.get('warning') else '' # Just use the emoji symbol in quotes, don't try to be clever.
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
input_box.pack(fill=tk.X, padx=8, pady=(12,6))

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

# Simple in-memory state
current_candidates = []

# Tooltip descriptions 
option_tooltips = {
    r'Digits \\d': r'Convert examples made only of digits to \\d{min,max}',
    r'Words \\w': r'Convert word tokens to \\w+',
    r'Whitespace \\s': r'Convert spaces/tabs to \\s+',
    'Repetitions': 'Detect repeated substrings like abcabc -> (?:abc){2}',
    'Capturing Groups': 'Use capturing groups instead of non-capturing',
    'Verbose Mode': 'Set the (?x) verbose flag for readability',
    'Case Insensitive': 'Use case-insensitive matching',
    'Start Anchor ^': 'Include start anchor ^ (toggle)',
    'End Anchor $': 'Include end anchor $ (toggle)'
}

# Options organized by section
options_sections = {
    'Character Conversions': [
        ("Digits \\d", digits_var),
        ("Words \\w", words_var),
        ("Whitespace \\s", whitespace_var),
    ],
    'Pattern Matching': [
        ("Repetitions", repetitions_var),
        ("Capturing Groups", capturing_var),
        ("Verbose Mode", verbose_var),
        ("Case Insensitive", case_var),
    ],
    'Anchors': [
        ("Start Anchor ^", start_anchor_var),
        ("End Anchor $", end_anchor_var),
    ]
}

# Create organized options UI
options_frame = tk.Frame(root)
options_frame.pack(fill=tk.X, padx=8, pady=8)

for section_name, options in options_sections.items():
    section_frame = ttk.LabelFrame(options_frame, text=section_name, padding=4)
    section_frame.pack(fill=tk.X, padx=4, pady=4)
    
    for text, var in options:
        w = ttk.Checkbutton(section_frame, text=text, variable=var)
        w.pack(side=tk.LEFT, padx=4)
        tip_text = option_tooltips.get(text, '')
        if tip_text:
            Tooltip(w, tip_text)


# Candidate list and preview
candidates_frame = tk.Frame(root)
candidates_frame.pack(fill=tk.BOTH, expand=True, pady=(6,0))

left = tk.Frame(candidates_frame)
left.pack(side=tk.LEFT, fill=tk.Y, padx=(4,6))

ttk.Label(right, text='Preview / Matches').pack()
preview_box = scrolledtext.ScrolledText(right, height=8, width=50, state='disabled')
preview_box.pack(fill=tk.BOTH, expand=True)


def show_candidate_details(event=None):
    # Hook selection
    sel = candidates_tree.selection()

    iid = sel[0]
    idx = int(iid)
    cand = current_candidates[idx]
    
    # Show match results
    preview_box.config(state='normal')
    preview_box.delete('1.0', tk.END)
    preview_box.insert(tk.END, f"Reason: {cand['reason']}\n")
    
    if cand['warning']:
        preview_box.insert(tk.END, f"Warning: {cand['warning']}\n")
        
    preview_box.insert(tk.END, "\nMatches:\n")
    
    for s, m in zip(input_box.get('1.0', tk.END).strip().splitlines(), cand['matches']):
        preview_box.insert(tk.END, f"  {s}  ->  {'MATCH' if m else 'NO MATCH'}\n")
        
    # Show simple generated counterexamples


    
# Status bar: shows tooltip/help text for controls
status_var = tk.StringVar(value='')
status_label = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor='w')
status_label.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()


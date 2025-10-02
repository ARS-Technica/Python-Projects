import tkinter as tk
from tkinter import ttk, scrolledtext

from regex_builder import RegExpBuilder
from trie import Trie

import re
from regex_builder import RegExpConfig


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

    regex = builder.build()
    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, regex)
    output_box.config(state='disabled')

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

import tkinter as tk
from tkinter import ttk, scrolledtext

from regex_builder import RegExpBuilder
from trie import Trie

import re
from regex_builder import RegExpConfig


def generate_button_action():
    input_text = input_box.get("1.0", tk.END).strip().splitlines()
    builder = RegExpBuilder.from_test_cases(input_text)
 
    regex = builder.build()
    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, regex)
    output_box.config(state='disabled')

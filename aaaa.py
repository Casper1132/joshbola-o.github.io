import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from lark import Lark, UnexpectedInput, UnexpectedToken

GRAMMAR = r"""
?start: expr

?expr: expr "+" term   -> add
     | expr "-" term   -> sub
     | term

?term: term "*" factor -> mul
     | term "/" factor -> div
     | factor

?factor: "-" factor    -> neg
       | NUMBER        -> number
       | "(" expr ")"

%import common.NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
"""

parser = Lark(GRAMMAR, start="start", parser="lalr")

def validate_expression(expr: str):
    """
    Returns (is_valid:bool, error:str or None)
    """
    try:
        parser.parse(expr)
        return True, None
    except UnexpectedToken as ut:
        return False, f"Unexpected token at position {ut.pos_in_stream}: {ut}"
    except UnexpectedInput as ui:
        # Generic unexpected input (includes incomplete)
        return False, f"Invalid input at position {ui.pos_in_stream}: {ui}"
    except Exception as e:
        return False, str(e)

# --------------------------------------------------
# GUI
# --------------------------------------------------
class CFGValidatorApp:
    def __init__(self, root):
        self.root = root
        root.title("CFG Arithmetic Expression Validator")
        root.geometry("700x460")
        root.resizable(False, False)

        # Frame: input
        frame_top = ttk.Frame(root, padding=(12, 12))
        frame_top.pack(fill="x")

        ttk.Label(frame_top, text="Enter arithmetic expression:").pack(anchor="w")
        self.input_var = tk.StringVar()
        self.entry = ttk.Entry(frame_top, textvariable=self.input_var, width=90)
        self.entry.pack(fill="x", pady=(6, 6))
        self.entry.bind("<Return>", lambda e: self.check())

        btn_frame = ttk.Frame(frame_top)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Validate", command=self.check).pack(side="left")
        ttk.Button(btn_frame, text="Clear", command=self.clear).pack(side="left", padx=(8,0))
        ttk.Button(btn_frame, text="Example", command=self.insert_example).pack(side="left", padx=(8,0))

        # Frame: results
        frame_mid = ttk.Frame(root, padding=(12, 6))
        frame_mid.pack(fill="both", expand=True)
        ttk.Label(frame_mid, text="Result:").pack(anchor="w")
        self.result_box = scrolledtext.ScrolledText(frame_mid, height=8, wrap="word", state="disabled")
        self.result_box.pack(fill="both", expand=True, pady=(6,6))

        # Frame: grammar & notes
        frame_bot = ttk.Frame(root, padding=(12, 6))
        frame_bot.pack(fill="both")
        ttk.Label(frame_bot, text="Grammar (EBNF):").pack(anchor="w")
        grammar_display = scrolledtext.ScrolledText(frame_bot, height=9, wrap="word", state="disabled")
        grammar_display.pack(fill="both", expand=False, pady=(6,0))
        grammar_display.configure(state="normal")
        grammar_display.insert("end", GRAMMAR)
        grammar_display.configure(state="disabled")

        # Status bar
        self.status = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom")

    def append_result(self, text: str):
        self.result_box.configure(state="normal")
        self.result_box.insert("end", text + "\n")
        self.result_box.see("end")
        self.result_box.configure(state="disabled")

    def check(self):
        expr = self.input_var.get().strip()
        if not expr:
            messagebox.showinfo("Empty input", "Please enter an expression to validate.")
            return
        valid, err = validate_expression(expr)
        if valid:
            self.status.set("Valid expression")
            self.append_result(f"[OK] {expr}")
        else:
            self.status.set("Invalid expression")
            self.append_result(f"[ERROR] {expr} -> {err}")

    def clear(self):
        self.input_var.set("")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.configure(state="disabled")
        self.status.set("Cleared")

    def insert_example(self):
        examples = [
            "1+2*3",
            "(4 - 5) * (6 + 7)",
            "-(3+2)*4",
            "42",
            "3 + * 4",         # invalid
            "(1+2"             # invalid
        ]
        # pick first valid example by default
        self.input_var.set(examples[0])
        self.status.set("Inserted example")

if __name__ == "__main__":
    root = tk.Tk()
    app = CFGValidatorApp(root)
    root.mainloop()

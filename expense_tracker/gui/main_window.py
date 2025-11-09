import tkinter as tk
from tkinter import ttk, messagebox

from expense_tracker.core.repository import TransactionRepository
from expense_tracker.gui.dialogs.add_expense import AddExpenseDialog
from expense_tracker.gui.dialogs.upload import UploadDialog


class MainWindow(tk.Frame):
    def __init__(self, master, repo):
        super().__init__(master)
        self.repo: TransactionRepository = repo
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.selected = None
        self._build_toolbar()
        self._build_body()
        self.refresh()


    def _build_body(self):
        self.tree = ttk.Treeview(self, columns=("id", "date", "amount", "category", "description"), show="headings")
        self.tree.heading("date", text="Date")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.column("id", width=0, stretch=tk.NO)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind('<ButtonRelease-1>', self.select_item)
        self.tree.bind('<Double-1>', lambda e: self._edit_transaction())

    
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in self.repo.get_all_transactions():
            self.tree.insert("", tk.END, values=(r["id"], r["date"], r["amount"], r["category"], r["description"]))
    
    def _build_toolbar(self):
        bar = tk.Frame(self)
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="Add Transaction", command=self._add_transaction).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Edit Transaction", command=self._edit_transaction).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Delete Transaction", command=self._delete_transaction).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Import Statement", command=self._upload_statement).pack(side=tk.RIGHT, padx=5, pady=5)
        self.qvar = tk.StringVar()
        ttk.Entry(bar, textvariable=self.qvar, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Search", command=self._search_transactions).pack(side=tk.LEFT, padx=5, pady=5)
        

    def select_item(self, event):
        item = self.tree.focus()
        if item:
            self.selected = self.tree.item(item, "values")

    def _upload_statement(self):
        dialog = UploadDialog(self.master, self.repo)
        self.master.wait_window(dialog)
        self.refresh()

    def _add_transaction(self):
        dialog = AddExpenseDialog(self.master, self.repo)
        self.master.wait_window(dialog)
        self.refresh()

    def _edit_transaction(self):
        if not self.selected:
            messagebox.showwarning("No selection", "Please select a transaction to edit.")
            return
        messagebox.showinfo("Edit Transaction", "Editing transaction with ID: {}".format(self.selected[0]))
    
    def _delete_transaction(self):
        if not self.selected:
            messagebox.showwarning("No selection", "Please select a transaction to delete.")
            return

        transaction_id = self.selected[0]
        details = f"ID: {self.selected[0]}\nDate: {self.selected[1]}\nAmount: {self.selected[2]}\nCategory: {self.selected[3]}\nDescription: {self.selected[4]}"
        
        confirm = messagebox.askyesno(
            "Delete Transaction", 
            f"Are you sure you want to delete the following transaction?\n\n{details}"
        )

        if confirm:
            self.repo.delete_transaction(transaction_id)
            messagebox.showinfo("Success", "Transaction deleted successfully.")
            self.refresh()
            self.selected = None

    def _search_transactions(self):
        query = self.qvar.get()
        messagebox.showinfo("Search Transactions", f"Search for: {query}")
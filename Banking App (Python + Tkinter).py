import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json
import os

# -----------------------------
# Domain model
# -----------------------------

@dataclass
class Transaction:
    timestamp: str
    type: str
    amount: float
    note: str = ""

@dataclass
class Account:
    account_id: str
    holder_name: str
    balance: float = 0.0
    history: List[Transaction] = field(default_factory=list)

    def deposit(self, amount: float, note: str = ""):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.history.append(Transaction(
            timestamp=_now(),
            type="DEPOSIT",
            amount=amount,
            note=note
        ))

    def withdraw(self, amount: float, note: str = ""):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        self.history.append(Transaction(
            timestamp=_now(),
            type="WITHDRAW",
            amount=amount,
            note=note
        ))

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Bank:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def create_account(self, account_id: str, holder_name: str, initial_deposit: float = 0.0):
        if not account_id.strip():
            raise ValueError("Account ID cannot be empty.")
        if not holder_name.strip():
            raise ValueError("Holder name cannot be empty.")
        if account_id in self.accounts:
            raise ValueError("Account ID already exists.")
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")
        acc = Account(account_id=account_id.strip(), holder_name=holder_name.strip())
        if initial_deposit > 0:
            acc.deposit(initial_deposit, note="Initial deposit")
        self.accounts[acc.account_id] = acc
        return acc

    def get_account(self, account_id: str) -> Account:
        if account_id not in self.accounts:
            raise ValueError("Account not found.")
        return self.accounts[account_id]

    def transfer(self, from_id: str, to_id: str, amount: float, note: str = ""):
        if from_id == to_id:
            raise ValueError("Source and destination accounts must differ.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        src = self.get_account(from_id)
        dst = self.get_account(to_id)
        if amount > src.balance:
            raise ValueError("Insufficient funds in source account.")
        # Perform transfer
        src.balance -= amount
        src.history.append(Transaction(
            timestamp=_now(),
            type="TRANSFER_OUT",
            amount=amount,
            note=f"To {to_id}. {note}".strip()
        ))
        dst.balance += amount
        dst.history.append(Transaction(
            timestamp=_now(),
            type="TRANSFER_IN",
            amount=amount,
            note=f"From {from_id}. {note}".strip()
        ))

    # Optional simple persistence
    def save_to_file(self, path: str):
        data = {
            "accounts": [
                {
                    "account_id": acc.account_id,
                    "holder_name": acc.holder_name,
                    "balance": acc.balance,
                    "history": [
                        {
                            "timestamp": t.timestamp,
                            "type": t.type,
                            "amount": t.amount,
                            "note": t.note
                        } for t in acc.history
                    ]
                } for acc in self.accounts.values()
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.accounts.clear()
        for acc in data.get("accounts", []):
            a = Account(
                account_id=acc["account_id"],
                holder_name=acc["holder_name"],
                balance=float(acc.get("balance", 0.0))
            )
            for t in acc.get("history", []):
                a.history.append(Transaction(
                    timestamp=t["timestamp"],
                    type=t["type"],
                    amount=float(t["amount"]),
                    note=t.get("note", "")
                ))
            self.accounts[a.account_id] = a

# -----------------------------
# Tkinter GUI
# -----------------------------

class BankingApp(tk.Tk):
    def __init__(self, bank: Bank, data_file: Optional[str] = None):
        super().__init__()
        self.title("Simple Banking App")
        self.geometry("900x600")
        self.bank = bank
        self.data_file = data_file

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_menu()
        self._build_notebook()

        # Load persisted data if available
        if self.data_file:
            try:
                self.bank.load_from_file(self.data_file)
            except Exception as e:
                messagebox.showwarning("Load failed", f"Could not load data: {e}")
        self._refresh_all_views()

        # Save on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self._save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def _build_notebook(self):
        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        # Tabs
        self.tab_create = ttk.Frame(nb)
        self.tab_deposit_withdraw = ttk.Frame(nb)
        self.tab_transfer = ttk.Frame(nb)
        self.tab_accounts = ttk.Frame(nb)
        self.tab_history = ttk.Frame(nb)

        nb.add(self.tab_create, text="Create account")
        nb.add(self.tab_deposit_withdraw, text="Deposit / Withdraw")
        nb.add(self.tab_transfer, text="Transfer")
        nb.add(self.tab_accounts, text="Accounts & balances")
        nb.add(self.tab_history, text="Transaction history")

        # Build each tab
        self._build_create_tab()
        self._build_deposit_withdraw_tab()
        self._build_transfer_tab()
        self._build_accounts_tab()
        self._build_history_tab()

    # ---- Create Account Tab ----
    def _build_create_tab(self):
        frame = self.tab_create
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Account ID:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(frame, text="Holder name:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(frame, text="Initial deposit:").grid(row=2, column=0, padx=8, pady=8, sticky="e")

        self.entry_acc_id = ttk.Entry(frame)
        self.entry_holder = ttk.Entry(frame)
        self.entry_initial = ttk.Entry(frame)

        self.entry_acc_id.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.entry_holder.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        self.entry_initial.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        btn_create = ttk.Button(frame, text="Create account", command=self._create_account)
        btn_create.grid(row=3, column=1, padx=8, pady=16, sticky="e")

    def _create_account(self):
        acc_id = self.entry_acc_id.get().strip()
        holder = self.entry_holder.get().strip()
        initial_str = self.entry_initial.get().strip()
        try:
            initial = float(initial_str) if initial_str else 0.0
            acc = self.bank.create_account(acc_id, holder, initial)
            messagebox.showinfo("Success", f"Account '{acc.account_id}' created for {acc.holder_name}.")
            self.entry_acc_id.delete(0, tk.END)
            self.entry_holder.delete(0, tk.END)
            self.entry_initial.delete(0, tk.END)
            self._refresh_all_views()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Deposit / Withdraw Tab ----
    def _build_deposit_withdraw_tab(self):
        frame = self.tab_deposit_withdraw
        for i in range(2):
            frame.columnconfigure(i, weight=1)

        # Left: Deposit
        deposit_frame = ttk.LabelFrame(frame, text="Deposit")
        deposit_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(deposit_frame, text="Account ID:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(deposit_frame, text="Amount:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(deposit_frame, text="Note:").grid(row=2, column=0, padx=8, pady=8, sticky="e")

        self.entry_dep_id = ttk.Entry(deposit_frame)
        self.entry_dep_amt = ttk.Entry(deposit_frame)
        self.entry_dep_note = ttk.Entry(deposit_frame)

        self.entry_dep_id.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.entry_dep_amt.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        self.entry_dep_note.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Button(deposit_frame, text="Deposit", command=self._do_deposit).grid(row=3, column=1, padx=8, pady=12, sticky="e")

        # Right: Withdraw
        withdraw_frame = ttk.LabelFrame(frame, text="Withdraw")
        withdraw_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(withdraw_frame, text="Account ID:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(withdraw_frame, text="Amount:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(withdraw_frame, text="Note:").grid(row=2, column=0, padx=8, pady=8, sticky="e")

        self.entry_wdr_id = ttk.Entry(withdraw_frame)
        self.entry_wdr_amt = ttk.Entry(withdraw_frame)
        self.entry_wdr_note = ttk.Entry(withdraw_frame)

        self.entry_wdr_id.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.entry_wdr_amt.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        self.entry_wdr_note.grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Button(withdraw_frame, text="Withdraw", command=self._do_withdraw).grid(row=3, column=1, padx=8, pady=12, sticky="e")

    def _do_deposit(self):
        acc_id = self.entry_dep_id.get().strip()
        amt_str = self.entry_dep_amt.get().strip()
        note = self.entry_dep_note.get().strip()
        try:
            amt = float(amt_str)
            acc = self.bank.get_account(acc_id)
            acc.deposit(amt, note)
            messagebox.showinfo("Success", f"Deposited {amt:.2f} to {acc.account_id}.")
            self.entry_dep_amt.delete(0, tk.END)
            self.entry_dep_note.delete(0, tk.END)
            self._refresh_all_views()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _do_withdraw(self):
        acc_id = self.entry_wdr_id.get().strip()
        amt_str = self.entry_wdr_amt.get().strip()
        note = self.entry_wdr_note.get().strip()
        try:
            amt = float(amt_str)
            acc = self.bank.get_account(acc_id)
            acc.withdraw(amt, note)
            messagebox.showinfo("Success", f"Withdrew {amt:.2f} from {acc.account_id}.")
            self.entry_wdr_amt.delete(0, tk.END)
            self.entry_wdr_note.delete(0, tk.END)
            self._refresh_all_views()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Transfer Tab ----
    def _build_transfer_tab(self):
        frame = self.tab_transfer
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="From account ID:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(frame, text="To account ID:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(frame, text="Amount:").grid(row=2, column=0, padx=8, pady=8, sticky="e")
        ttk.Label(frame, text="Note:").grid(row=3, column=0, padx=8, pady=8, sticky="e")

        self.entry_tr_from = ttk.Entry(frame)
        self.entry_tr_to = ttk.Entry(frame)
        self.entry_tr_amt = ttk.Entry(frame)
        self.entry_tr_note = ttk.Entry(frame)

        self.entry_tr_from.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.entry_tr_to.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        self.entry_tr_amt.grid(row=2, column=1, padx=8, pady=8, sticky="ew")
        self.entry_tr_note.grid(row=3, column=1, padx=8, pady=8, sticky="ew")

        ttk.Button(frame, text="Transfer", command=self._do_transfer).grid(row=4, column=1, padx=8, pady=12, sticky="e")

    def _do_transfer(self):
        from_id = self.entry_tr_from.get().strip()
        to_id = self.entry_tr_to.get().strip()
        amt_str = self.entry_tr_amt.get().strip()
        note = self.entry_tr_note.get().strip()
        try:
            amt = float(amt_str)
            self.bank.transfer(from_id, to_id, amt, note)
            messagebox.showinfo("Success", f"Transferred {amt:.2f} from {from_id} to {to_id}.")
            self.entry_tr_amt.delete(0, tk.END)
            self.entry_tr_note.delete(0, tk.END)
            self._refresh_all_views()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Accounts & Balances Tab ----
    def _build_accounts_tab(self):
        frame = self.tab_accounts
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = ("account_id", "holder_name", "balance")
        self.tree_accounts = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_accounts.heading(col, text=col.replace("_", " ").title())
            self.tree_accounts.column(col, width=200, anchor="center")
        self.tree_accounts.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_accounts.yview)
        self.tree_accounts.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Quick balance lookup
        lookup_frame = ttk.LabelFrame(frame, text="Quick balance lookup")
        lookup_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        lookup_frame.columnconfigure(1, weight=1)

        ttk.Label(lookup_frame, text="Account ID:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.entry_lookup_id = ttk.Entry(lookup_frame)
        self.entry_lookup_id.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        ttk.Button(lookup_frame, text="Check balance", command=self._check_balance).grid(row=0, column=2, padx=8, pady=8)

    def _check_balance(self):
        acc_id = self.entry_lookup_id.get().strip()
        try:
            acc = self.bank.get_account(acc_id)
            messagebox.showinfo("Balance", f"Account {acc.account_id} ({acc.holder_name}) balance: {acc.balance:.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Transaction History Tab ----
    def _build_history_tab(self):
        frame = self.tab_history
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        filter_frame = ttk.LabelFrame(frame, text="Select account")
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filter_frame.columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Account ID:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.combo_hist_id = ttk.Combobox(filter_frame, values=[], state="readonly")
        self.combo_hist_id.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        ttk.Button(filter_frame, text="Load history", command=self._load_history).grid(row=0, column=2, padx=8, pady=8)

        columns = ("timestamp", "type", "amount", "note")
        self.tree_history = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree_history.heading(col, text=col.title())
            self.tree_history.column(col, width=180 if col != "note" else 300, anchor="center")
        self.tree_history.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_history.yview)
        self.tree_history.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

    def _load_history(self):
        acc_id = self.combo_hist_id.get().strip()
        self.tree_history.delete(*self.tree_history.get_children())
        if not acc_id:
            return
        try:
            acc = self.bank.get_account(acc_id)
            for t in acc.history:
                self.tree_history.insert("", "end", values=(t.timestamp, t.type, f"{t.amount:.2f}", t.note))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---- Refresh / Save / Close ----
    def _refresh_all_views(self):
        # Refresh accounts list
        self.tree_accounts.delete(*self.tree_accounts.get_children())
        for acc in self.bank.accounts.values():
            self.tree_accounts.insert("", "end", values=(acc.account_id, acc.holder_name, f"{acc.balance:.2f}"))

        # Refresh combobox options
        acc_ids = list(self.bank.accounts.keys())
        self.combo_hist_id["values"] = acc_ids

    def _save(self):
        if not self.data_file:
            messagebox.showinfo("Info", "No data file configured. Launch with a path or modify the code to set one.")
            return
        try:
            self.bank.save_to_file(self.data_file)
            messagebox.showinfo("Saved", f"Data saved to {self.data_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

    def _on_close(self):
        try:
            if self.data_file:
                self.bank.save_to_file(self.data_file)
        except Exception:
            pass
        self.destroy()

# -----------------------------
# Entry point
# -----------------------------

def main():
    bank = Bank()
    # Optional: set a data file for persistence in the current directory
    data_file = "bank_data.json"
    app = BankingApp(bank, data_file=data_file)
    app.mainloop()

if __name__ == "__main__":
    main()
    
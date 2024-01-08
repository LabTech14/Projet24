import tkinter as tk
from tkinter import messagebox
import sqlite3

# Initialisation de la base de données
conn = sqlite3.connect('bank.db')
c = conn.cursor()

# Créer la table des transactions si elle n'existe pas
c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number TEXT NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL, -- 'credit' or 'debit'
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Fonctions pour gérer les transactions
def add_transaction(account_number, amount, transaction_type):
    c.execute('INSERT INTO transactions (account_number, amount, transaction_type) VALUES (?, ?, ?)',
              (account_number, amount, transaction_type))
    conn.commit()

# Interface utilisateur
root = tk.Tk()
root.title("Gestion des transactions bancaires")

# Widgets pour les transactions
account_label = tk.Label(root, text="Numéro de compte")
account_label.pack()
account_entry = tk.Entry(root)
account_entry.pack()

amount_label = tk.Label(root, text="Montant")
amount_label.pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

# Fonctions pour les boutons
def credit():
    account = account_entry.get()
    amount = amount_entry.get()
    add_transaction(account, amount, 'credit')
    messagebox.showinfo("Succès", "Crédit ajouté avec succès")

def debit():
    account = account_entry.get()
    amount = amount_entry.get()
    add_transaction(account, amount, 'debit')
    messagebox.showinfo("Succès", "Débit ajouté avec succès")

credit_button = tk.Button(root, text="Créditer", command=credit)
credit_button.pack()

debit_button = tk.Button(root, text="Débiter", command=debit)
debit_button.pack()

root.mainloop()

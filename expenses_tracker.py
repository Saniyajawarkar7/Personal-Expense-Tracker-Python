import customtkinter as ctk
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from CTkMessagebox import CTkMessagebox
from datetime import datetime
import os

# --- File Setup ---
FILE_NAME = "expenses.csv"
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

# --- App Setup ---
ctk.set_appearance_mode("dark")  # or "light"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("💸 Personal Expense Tracker")
app.geometry("700x750")

# --- Header ---
header = ctk.CTkLabel(app, text="💸 Personal Expense Tracker", font=("Poppins Bold", 26))
header.pack(pady=20)

# --- Input Frame ---
frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(padx=20, pady=10, fill="x")

ctk.CTkLabel(frame, text="Date (YYYY-MM-DD):", font=("Poppins", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
ctk.CTkLabel(frame, text="Category:", font=("Poppins", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
ctk.CTkLabel(frame, text="Description:", font=("Poppins", 16)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
ctk.CTkLabel(frame, text="Amount (₹):", font=("Poppins", 16)).grid(row=3, column=0, padx=10, pady=10, sticky="e")

date_entry = ctk.CTkEntry(frame, placeholder_text=datetime.now().strftime("%Y-%m-%d") + " (Leave blank for today)")
date_entry.grid(row=0, column=1, padx=10, pady=10)

categories = [
    "Housing", "Utilities", "Groceries", "Dining Out", "Transportation", "Healthcare",
    "Entertainment", "Shopping", "Debt/Loans", "Insurance", "Education", "Savings", "Other"
]
category = ctk.CTkOptionMenu(frame, values=categories)
category.grid(row=1, column=1, padx=10, pady=10)

description = ctk.CTkEntry(frame, placeholder_text="Enter details")
description.grid(row=2, column=1, padx=10, pady=10)

amount = ctk.CTkEntry(frame, placeholder_text="Enter amount")
amount.grid(row=3, column=1, padx=10, pady=10)

# --- Functions ---
def add_expense():
    global df
    cat = category.get()
    desc = description.get()
    amt_str = amount.get()
    date_str = date_entry.get()

    if cat and desc and amt_str:
        if not date_str:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                date = date_str
            except ValueError:
                CTkMessagebox(title="Error", message="Invalid date format. Use YYYY-MM-DD.", icon="cancel")
                return

        try:
            amt = float(amt_str)
            df.loc[len(df)] = [date, cat, desc, amt]
            df.to_csv(FILE_NAME, index=False)

            CTkMessagebox(title="Success", message=f"Expense added successfully for {date}!", icon="check")

            date_entry.delete(0, "end")
            description.delete(0, "end")
            amount.delete(0, "end")
            category.set(categories[0])

        except ValueError:
            CTkMessagebox(title="Error", message="Amount must be numeric.", icon="cancel")
    else:
        CTkMessagebox(title="Warning", message="Please fill all fields!", icon="warning")

def manage_expenses_window():
    """Open a window to view and delete individual expenses."""
    global df
    if len(df) == 0:
        CTkMessagebox(title="Info", message="No records found to manage.", icon="info")
        return

    manage_window = ctk.CTkToplevel(app)
    manage_window.title("🗑️ Manage Expenses")
    manage_window.geometry("800x600")
    manage_window.grab_set()

    control_frame = ctk.CTkFrame(manage_window)
    control_frame.pack(padx=20, pady=10, fill="x")

    ctk.CTkLabel(control_frame, text="Row Index to Delete:", font=("Poppins", 16)).pack(side="left", padx=(10, 5))
    index_entry = ctk.CTkEntry(control_frame, width=80, placeholder_text="e.g., 5")
    index_entry.pack(side="left", padx=(0, 15))

    def update_table_view():
        text_widget.delete("1.0", "end")
        table_string = df.to_string(index=True, header=True)
        text_widget.insert("1.0", table_string)

    def delete_selected_row():
        global df
        index_to_delete_str = index_entry.get().strip()

        if not index_to_delete_str:
            CTkMessagebox(title="Warning", message="Enter an index to delete.", icon="warning")
            return

        try:
            index_to_delete = int(index_to_delete_str)
        except ValueError:
            CTkMessagebox(title="Error", message="Index must be a number.", icon="cancel")
            return

        if index_to_delete in df.index:
            confirm = CTkMessagebox(
                title="Confirm Deletion",
                message=f"Delete expense at index {index_to_delete}?",
                icon="question",
                option_1="Cancel",
                option_2="Confirm Delete"
            )
            if confirm.get() == "Confirm Delete":
                df = df.drop(index=index_to_delete).reset_index(drop=True)
                df.to_csv(FILE_NAME, index=False)
                CTkMessagebox(title="Success", message="Expense deleted.", icon="check")
                update_table_view()
        else:
            CTkMessagebox(title="Error", message="Invalid index.", icon="cancel")

    delete_btn = ctk.CTkButton(control_frame, text="🗑️ Delete Row", command=delete_selected_row, fg_color="#E74C3C")
    delete_btn.pack(side="left", padx=10)

    text_widget = ctk.CTkTextbox(manage_window, width=760, height=450, font=("Consolas", 12))
    text_widget.pack(padx=20, pady=10)
    update_table_view()

def show_category_chart():
    if len(df) == 0:
        CTkMessagebox(title="Info", message="No data to display.", icon="info")
        return
    plt.figure(figsize=(8, 8))
    df.groupby("Category")["Amount"].sum().plot.pie(
        autopct="%1.1f%%", startangle=90, colors=sns.color_palette("Set3")
    )
    plt.title("Expense Distribution by Category", fontsize=14)
    plt.ylabel("")
    plt.show()

def show_monthly_chart():
    if len(df) == 0:
        CTkMessagebox(title="Info", message="No data to display.", icon="info")
        return

    df_temp = df.copy()
    df_temp["Date"] = pd.to_datetime(df_temp["Date"])
    df_temp["Month"] = df_temp["Date"].dt.to_period('M')
    monthly_summary = df_temp.groupby("Month")["Amount"].sum().reset_index()
    monthly_summary["Month_Label"] = monthly_summary["Month"].astype(str)

    plt.figure(figsize=(10, 6))
    sns.lineplot(x="Month_Label", y="Amount", data=monthly_summary, marker="o", linewidth=2.5)
    plt.title("Monthly Spending Trend", fontsize=14)
    plt.xlabel("Month (YYYY-MM)")
    plt.ylabel("Total Spending (₹)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def show_average_expense():
    """Show average expenditure using NumPy."""
    if len(df) == 0:
        CTkMessagebox(title="Info", message="No data available to calculate average.", icon="info")
        return

    amounts = np.array(df["Amount"])
    avg = np.mean(amounts)
    high = np.max(amounts)
    low = np.min(amounts)
    total = np.sum(amounts)

    CTkMessagebox(
        title="Expense Summary (NumPy)",
        message=f"💰 Average: ₹{avg:.2f}\n📈 Highest: ₹{high:.2f}\n📉 Lowest: ₹{low:.2f}\n💵 Total: ₹{total:.2f}",
        icon="info"
    )

def delete_all_expenses():
    global df
    confirm = CTkMessagebox(
        title="Confirm Deletion",
        message="Delete ALL recorded expenses? This cannot be undone.",
        icon="warning",
        option_1="Cancel",
        option_2="Yes, Delete All"
    )
    if confirm.get() == "Yes, Delete All":
        df = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
        df.to_csv(FILE_NAME, index=False)
        CTkMessagebox(title="Deleted", message="All expenses deleted.", icon="check")

# --- Buttons ---
button_frame = ctk.CTkFrame(app, corner_radius=15)
button_frame.pack(pady=20)

add_btn = ctk.CTkButton(button_frame, text="Add Expense", command=add_expense, width=180, height=40)
view_btn = ctk.CTkButton(button_frame, text="View/Delete Table", command=manage_expenses_window, width=180, height=40)
cat_btn = ctk.CTkButton(button_frame, text="Category Chart", command=show_category_chart, width=180, height=40)
month_btn = ctk.CTkButton(button_frame, text="Monthly Chart", command=show_monthly_chart, width=180, height=40)
avg_btn = ctk.CTkButton(button_frame, text="💰 Average Expense", command=show_average_expense, width=180, height=40)
delete_btn = ctk.CTkButton(button_frame, text="❌ Delete All", command=delete_all_expenses, width=180, height=40, fg_color="#E74C3C")

add_btn.grid(row=0, column=0, padx=10, pady=10)
view_btn.grid(row=0, column=1, padx=10, pady=10)
cat_btn.grid(row=1, column=0, padx=10, pady=10)
month_btn.grid(row=1, column=1, padx=10, pady=10)
avg_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
delete_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

app.mainloop()

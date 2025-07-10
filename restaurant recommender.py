import pandas as pd
from sklearn.preprocessing import LabelEncoder
import tkinter as tk
from tkinter import ttk, messagebox
import os
import webbrowser

df = pd.read_csv("restaurant_data.xlsx.csv")
df.columns = df.columns.str.strip()
df.dropna(subset=['Cuisines'], inplace=True)

df = df[['Restaurant Name', 'City', 'Cuisines', 'Price range', 'Has Table booking', 'Has Online delivery', 'Aggregate rating', 'Votes']]

city_options = sorted(df['City'].dropna().unique())
cuisine_options = sorted(df['Cuisines'].dropna().unique())
price_options = sorted(df['Price range'].dropna().unique())
yn_options = ['Yes', 'No']

root = tk.Tk()
root.title("Restaurant Recommender")
root.geometry("600x600")
root.configure(bg="#f0f0f5")

tk.Label(root, text="Select Your Preferences", font=("Arial", 18, "bold"), bg="#f0f0f5").pack(pady=10)

fields = {}
dropdowns = {}

def create_dropdown(label, options):
    frame = tk.Frame(root, bg="#f0f0f5")
    frame.pack(pady=5)
    tk.Label(frame, text=label + ":", font=("Arial", 12), width=20, anchor="w", bg="#f0f0f5").pack(side="left")
    var = tk.StringVar()
    combo = ttk.Combobox(frame, textvariable=var, values=options, state="readonly", width=30)
    combo.pack(side="left")
    dropdowns[label] = combo

create_dropdown("City", city_options)
create_dropdown("Cuisine", cuisine_options)
create_dropdown("Price Range", price_options)
create_dropdown("Has Online delivery", yn_options)
create_dropdown("Has Table booking", yn_options)

def recommend():
    try:
        city = dropdowns["City"].get()
        cuisine = dropdowns["Cuisine"].get()
        price = int(dropdowns["Price Range"].get())
        online = dropdowns["Has Online delivery"].get()
        booking = dropdowns["Has Table booking"].get()

        filtered = df[
            (df['City'] == city) &
            (df['Cuisines'].str.lower().str.contains(cuisine.lower())) &
            (df['Price range'] == price) &
            (df['Has Online delivery'].str.title() == online) &
            (df['Has Table booking'].str.title() == booking)
        ]

        if filtered.empty:
            messagebox.showinfo("No Match", "No restaurants match your preferences.")
        else:
            top_recommendations = filtered.sort_values(by=['Aggregate rating', 'Votes'], ascending=False).head(5)
            show_result(top_recommendations)
            save_to_excel(city, cuisine, price, online, booking, top_recommendations)

    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

def show_result(data):
    result_win = tk.Toplevel(root)
    result_win.title("Top Recommendations")
    result_win.geometry("520x300")
    result_win.configure(bg="#ffffff")

    tk.Label(result_win, text="Top Restaurant Recommendations", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

    txt = tk.Text(result_win, wrap="word", width=60, height=12)
    txt.pack(padx=10)
    for idx, row in data.iterrows():
        txt.insert("end", f"{row['Restaurant Name']} | {row['Cuisines']} | Rating: {row['Aggregate rating']}\n")

def save_to_excel(city, cuisine, price, online, booking, result_df):
    filename = "recommendation_history.xlsx"
    record = {
        'City': city,
        'Cuisine': cuisine,
        'Price range': price,
        'Online delivery': online,
        'Table booking': booking
    }

    history_data = []
    for idx, row in result_df.iterrows():
        history_data.append({
            **record,
            'Recommended Restaurant': row['Restaurant Name'],
            'Rating': row['Aggregate rating'],
            'Votes': row['Votes']
        })

    if os.path.exists(filename):
        old_df = pd.read_excel(filename)
        new_df = pd.concat([old_df, pd.DataFrame(history_data)], ignore_index=True)
    else:
        new_df = pd.DataFrame(history_data)

    new_df.to_excel(filename, index=False)

def view_history():
    file = "recommendation_history.xlsx"
    if os.path.exists(file):
        webbrowser.open(file)
    else:
        messagebox.showinfo("No History", "No recommendation history found yet.")

ttk.Button(root, text="Get Recommendation", command=recommend).pack(pady=15)
ttk.Button(root, text="View Recommendation History", command=view_history).pack(pady=5)

root.mainloop()

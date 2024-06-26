import tkinter as tk
from tkinter import messagebox, ttk, Button, PhotoImage, Canvas
from PIL import ImageTk, Image
from tkmacosx import Button
from database_code import *
import string
import uuid
import zipfile
import os

def fetch_dress_details(dress_name):
    # Replace 'your_database.db' with the actual path to your SQLite database file
    db_path = 'wedding_users.db'
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # SQL query to fetch dress details
    query = "SELECT upc, name, price, color,description FROM wedding_dress WHERE name = ?"
    cursor.execute(query, (dress_name,))
    dress_details = cursor.fetchone()
        
    connection.close()
    return dress_details if dress_details else ('', '', '', '')

def create_footer(master):
    # Footer frame
    footer_frame = tk.Frame(master, bg="#000000", pady=10)
    footer_frame.pack(side="bottom", fill="x")

    # Copyright label
    copyright_label = tk.Label(footer_frame, text="© 2024 H.E.M. All Rights Reserved", font=("Arial", 12),
                               fg="white", bg="#000000")
    copyright_label.pack()

    return footer_frame

class CheckoutPage:
    def __init__(self, master, username, upc):
        self.master = master
        self.username = username
        self.upc = upc
        self.master.title("Checkout")
        self.master.geometry("800x600")  # Adjusted height for better visibility
        self.master.configure(bg='#FDE1DE')

        # Fetch user data from the database
        self.user_data = fetch_user_data(username)
        self.entry_fields = {}
        self.labels = {}

        
        if self.user_data:
            # Display username in a better position
            username_label = tk.Label(self.master, text=f"Username: {self.user_data['username']}",
                                      font=("Brush Script MT", 20), bg='#FDE1DE', fg='black')
            username_label.pack(pady=10)

            # Adding more separation
            separator2 = tk.Frame(self.master, height=2, bd=1, relief="groove", bg='black')
            separator2.pack(fill="x", padx=20, pady=10)

            # Shipping Information
            shipping_label = tk.Label(self.master, text="Shipping Information", font=("Lucida Calligraphy", 24),
                                      bg="#FDE1DE", fg="black")
            shipping_label.pack(pady=20)

            address_label = tk.Label(self.master, text="Address", font=("Brush Script MT", 16), bg='#FDE1DE', fg='black')
            address_label.place(x=400 - 150, y=150 + 10, anchor="e")
            
            address_entry = tk.Entry(self.master, font=("Arial", 12), bg='white', fg='black')
            address_entry.place(x=400 - 100, y=150 + 10, anchor="w")

            address_button = tk.Button(self.master, text="Enter", bg='#FDE1DE', fg='black', font=("Lucida Calligraphy", 14))
            address_button.place(x=400 + 100, y=150 + 10, anchor="w")

            # Billing Information
            billing_label = tk.Label(self.master, text="Billing Information", font=("Lucida Calligraphy", 24),
                                      bg="#FDE1DE", fg="black")
            billing_label.pack(pady=40)

            row = 4
            payment_fields = ["credit_card_num", "CVC", "expiration_date"]
            for field in payment_fields:
                label = tk.Label(self.master, text=f"{field.replace('_', ' ').title()}: ",
                                 font=("Brush Script MT", 16),
                                 bg='#FDE1DE', fg='black')
                label.place(x=400 - 150, y=150 + row * 30, anchor="e")
                self.labels[field] = label


                entry = tk.Entry(self.master, font=("Arial", 12), bg='white', fg='black')
                entry.insert(0, self.user_data.get(field, ""))  # Insert data if available, else empty string
                entry.place(x=400 - 100, y=150 + row * 30, anchor="w")
                self.entry_fields[field] = entry

                edit_button = tk.Button(self.master, text="Enter", command=lambda k=field: self.update_payment_info(k),
                                        bg='#FDE1DE', fg='black', font=("Lucida Calligraphy", 14))
                edit_button.place(x=400 + 100, y=150 + row * 30, anchor="w")

                row += 1

        else:
            # Display message if user data is not found
            error_label = tk.Label(self.master, text="User data not found", font=("Arial", 20), bg='#FDE1DE', fg='red')
            error_label.pack(pady=20)

        # Create a label to display order status
        self.order_status_label = tk.Label(self.master, text="", font=("Lucida Calligraphy", 16), bg='#FDE1DE', fg='black')
        self.order_status_label.pack(pady=10)
        self.order_status_label.place(x=375, y=150 + (row + 2) * 30, anchor="n")

        # Place Order Button
        place_order_button = tk.Button(self.master, text="Place Order", command=self.place_order,
                                       font=("Lucida Calligraphy", 20), bg='#FDE1DE', fg='black')
        place_order_button.place(x=375, y=150 + (row + 3) * 30, anchor="n")

    def place_order(self):
        # Placeholder function to place the order
        print("Placing order...")
        # Here you would add the logic to insert the order into the database
        user_id = self.username  # Assuming the username serves as the user_id
        wedding_dress_upc = self.upc
        tracking_id = str(uuid.uuid4())[:18]  # Get the first 18 characters of the UUID
        arrival_status = "Pending"  # Set initial arrival status
        # Call the insert_order function to add the order to the database
        insert_order(user_id, wedding_dress_upc, tracking_id, arrival_status)
        
        self.order_status_label.config(text="Order placed successfully!")        
        
    def update_payment_info(self, field):
        entry = self.entry_fields[field]
        new_value = entry.get()
        if field in ["credit_card_num", "CVC", "expiration_date"]:
            update_user_data(self.username, field, new_value)
            self.labels[field].config(text=f"{field.replace('_', ' ').title()}: {new_value}")

        else:
            messagebox.showwarning("Warning", "Only payment-related fields can be updated here!")

class ProfilePage:
    def __init__(self, master, username):
        self.master = master
        self.master.title("User Profile")
        self.master.geometry("1280x800")  # Adjusted height for better visibility
        self.master.configure(bg='#FDE1DE')  # Cream background

        # Fetch user data from the database
        self.user_data = fetch_user_data(username)

        if self.user_data:
            # Display name and last name in a bigger font at the top center
            name_label = tk.Label(master, text=f"{self.user_data['first_name']} {self.user_data['last_name']}",
                                  font=("Lucida Calligraphy", 36), bg='#FDE1DE', fg='black')
            name_label.pack(pady=20)

            # Adding a line for separation
            separator1 = tk.Frame(master, height=2, bd=1, relief="groove", bg='black')
            separator1.pack(fill="x", padx=20, pady=10)

            # Display username in a better position
            username_label = tk.Label(master, text=f"Username: {self.user_data['username']}",
                                      font=("Brush Script MT", 20), bg='#FDE1DE', fg='black')
            username_label.pack(pady=10)

            # Adding more separation
            separator2 = tk.Frame(master, height=2, bd=1, relief="groove", bg='black')
            separator2.pack(fill="x", padx=20, pady=10)

            row = 2
            # Display the rest of the information in the middle of the page
            self.entry_fields = {}
            self.labels = {}
            for key, value in self.user_data.items():
                if key not in ["first_name", "last_name", "username", "payment_id"]:
                    label = tk.Label(master, text=f"{key.replace('_', ' ').title()}: ", font=("Brush Script MT", 16),
                                     bg='#FDE1DE', fg='black')
                    label.place(x=640 - 150, y=150 + row * 30, anchor="e")
                    self.labels[key] = label

                    entry = tk.Entry(master, font=("Arial", 12), bg='white', fg='black')
                    entry.insert(0, value if value else "")  # Placeholder for empty fields
                    entry.place(x=640 - 100, y=150 + row * 30, anchor="w")
                    self.entry_fields[key] = entry

                    edit_button = tk.Button(master, text="Edit", command=lambda k=key: self.edit_field(k),
                                            bg='#FDE1DE', fg='black', font=("Lucida Calligraphy", 14))
                    edit_button.place(x=640 + 100, y=150 + row * 30, anchor="w")

                    row += 1

            # Add payment information fields
            if 'payment_id' in self.user_data and self.user_data['payment_id']:
                payment_label = tk.Label(master, text="Payment Information", font=("Lucida Calligraphy", 20),
                                         bg='#FDE1DE', fg='black')
                payment_label.place(x=640, y=150 + row * 30, anchor="n")

                row += 1
                payment_fields = ["payment_id", "credit_card_num", "CVC", "expiration_date"]
                for field in payment_fields:
                    label = tk.Label(master, text=f"{field.replace('_', ' ').title()}: ",
                                     font=("Brush Script MT", 16),
                                     bg='#FDE1DE', fg='black')
                    label.place(x=640 - 150, y=150 + row * 30, anchor="e")
                    self.labels[field] = label

                    entry = tk.Entry(master, font=("Arial", 12), bg='white', fg='black')
                    entry.insert(0, self.user_data.get(field, ""))  # Insert data if available, else empty string
                    entry.place(x=640 - 100, y=150 + row * 30, anchor="w")
                    self.entry_fields[field] = entry

                    edit_button = tk.Button(master, text="Edit", command=lambda k=field: self.edit_field(k),
                                            bg='#FDE1DE', fg='black', font=("Lucida Calligraphy", 14))
                    edit_button.place(x=640 + 100, y=150 + row * 30, anchor="w")

                    row += 1

            window_width = master.winfo_width()

            # Adding a line for separation after payment information
            separator3 = Canvas(master, width=1280, height=2, bg='black', highlightthickness=0)
            separator3.create_line(0, 0, 1280, 0, fill='black', width=2)
            separator3.pack(pady=10)
            separator3.place(x=640, y=150 + 8 * 30, anchor="center")  # Adjusted position and font size
            
            # Adding "My Orders" label
            orders_label = tk.Label(master, text="Orders", font=("Lucida Calligraphy", 20), bg='#FDE1DE', fg='black')
            orders_label.pack(pady=10)
            orders_label.place(x=640, y=150 + 9 * 30, anchor="center")  # Adjusted position and font size
            

            # Adding a line for separation after payment information
            separator4 = Canvas(master, width=1280, height=2, bg='black', highlightthickness=0)
            separator4.create_line(0, 0, 1280, 0, fill='black', width=2)
            separator4.pack(pady=10)
            separator4.place(x=640, y=150 + 10 * 30, anchor="center")  # Adjusted position and font size


            # Fetch order data from the database
            self.order_data = fetch_order_data(username)

            if self.order_data:
               
                # Adjusting the starting row for order display
                row += 2
                # Display the order information in the middle of the page
                for order in self.order_data:
                    for key, value in order.items():
                        label = tk.Label(master, text=f"{key.replace('_', ' ').title()}: {value}",
                                         font=("Brush Script MT", 20), bg='#FDE1DE', fg='black')
                        label.place(x=640, y=150 + row * 30, anchor="center")  # Adjusted position and font size
                        row += 1

            else:
                # Display message if order data is not found
                error_label = tk.Label(master, text="No orders", font=("Arial", 20), bg='#FDE1DE', fg='black')
                error_label.pack(pady=20)
                error_label.place(x=640, y=150 + 12 * 30, anchor="center")  # Adjusted position and font size


        else:
            # Display message if user data is not found
            error_label = tk.Label(master, text="User data not found", font=("Arial", 20), bg='#FDE1DE', fg='red')
            error_label.pack(pady=20)

    def edit_field(self, field):
        entry = self.entry_fields[field]  # Retrieve the entry field associated with the edited value
        new_value = entry.get()
        update_user_data(self.user_data['username'], field, new_value)
        self.user_data[field] = new_value
        self.labels[field].config(text=f"{field.replace('_', ' ').title()}: {new_value}")

class MainPage:
    def __init__(self, master, username):
        self.master = master
        self.username = username  # Store username as an attribute
        self.master.title("Main Page")
        self.master.geometry("1280x1920")
        self.master.configure(bg='#FEF0EF')  # Cream background

        self.label = tk.Label(master, text="H.E.M.", font=("Lucida Calligraphy", 40), bg='#FEF0EF', fg='black')
        self.label.pack(pady=20)
        self.dress_data = {
            'LEONIE': '260235696944', 'BRYNLEE': '366054713060', 'RHYA': '765243351243',
            'HARMONIA': '573762794674', 'MEMPHIS': '247304459935', 'DORI': '223401317803',
            'CARMELLA': '734562441382', 'LUXIA': '549306732031', 'RAMONA': '570882701357',
            'ARACELY': '213175329642', 'BELLIMISA': '379570679859', 'MAIA': '716922330344',
            'TATITANA': '997242272963', 'AURORA': '313455989872', 'NEELA': '144691041532',
            'DOLORES': '532619135710', 'JOLENE': '204820886951', 'VARELLA': '669304145861',
            'SERAPHINE': '381006261038', 'IRIS': '828169952218'
        }

        # Set background color for the menu bar
        menu_bg_color = self.master.cget("bg")

        # Create a frame to hold the menu bar
        menu_frame = tk.Frame(master, bg=menu_bg_color)  # Add border and relief
        menu_frame.pack(side=tk.TOP, pady=10)

        # Create a dropdown button for the account
        self.account_menu = tk.Menubutton(menu_frame, text="Account", compound=tk.LEFT, bg=menu_bg_color, fg='black',
                                          font=("Brush Script MT", 18))
        self.account_menu.menu = tk.Menu(self.account_menu, tearoff=0)
        self.account_menu["menu"] = self.account_menu.menu

        # Add options to the account menu
        self.account_menu.menu.add_command(label="Profile", command=self.show_profile)
        self.account_menu.menu.add_command(label="Logout", command=self.logout)

        self.account_menu.pack(side=tk.RIGHT, padx=10)
        # Configure button style to remove button shape
        button_style = {"border": 1, "bg": menu_bg_color, "width": 13, "height": 2, "highlightbackground": "black",
                        "relief": "solid"}

    # At the class level
        self.vintage_dresses = ['LEONIE', 'BRYNLEE', 'HARMONIA', 'RHYA', 'DORI']
        self.princess_dresses = ['CARMELLA', 'LUXIA', 'RAMONA', 'ARACELY', 'BELLIMISA']
        self.boho_dresses = ['MAIA', 'DOLORES', 'TATITANA', 'AURORA', 'NEELA']
        self.elegant_dresses = ['JOLENE', 'MEMPHIS', 'VARELLA', 'SERAPHINE', 'IRIS']

        buttons_data = [
            ("Wedding Dresses",
             self.show_wedding_dresses),
            ("Collections", self.show_collections),
            ("Styles", self.show_styles),
            ("Reviews", self.show_reviews)
        ]

        # Create menu buttons
        for text, command in buttons_data:
            button = tk.Button(menu_frame, text=text, font=("Brush Script MT", 24),
                               command=command, **button_style)
            button.pack(side=tk.LEFT, padx=10)

        # Center the menu bar horizontally
        menu_frame.place(relx=.5, rely=.15, anchor=tk.CENTER)

        # Create a frame to hold the photo boxes
        photo_frame = tk.Frame(master, bg='#FEF0EF')
        photo_frame.pack(pady=20)
        photo_frame.place(relx=0.5, rely=0.58, anchor=tk.CENTER)

        # Placeholder images, replace with actual photo paths
        image_paths = ["media/VARELLA.png", "media/ARACELY.png"]

        for image_path in image_paths:
            img = Image.open(image_path)
            img = img.resize((400, 400))  # Resize the image
            photo = ImageTk.PhotoImage(img)

            # Create photo box
            photo_box = tk.Label(photo_frame, image=photo)
            photo_box.image = photo  # Store reference to prevent garbage collection
            photo_box.pack(side=tk.LEFT, padx=40)

        self.footer = create_footer(master)

        # Create a frame for reviews
        self.reviews_frame = tk.Frame(master, bg='#FEF0EF')
        self.reviews_frame.pack(pady=20)

        # Display reviews
        #self.show_reviews(master)

    def show_reviews(self):
        # Create a frame for the scrollable reviews
        reviews_frame = tk.Frame(self.master, bg='#FEF0EF')
        reviews_frame.pack(expand=True, fill=tk.BOTH, pady=20)

        # Create canvas
        canvas = tk.Canvas(reviews_frame, bg='#FEF0EF')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(reviews_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create scrollable inner frame
        scrollable_inner_frame = tk.Frame(canvas, bg='#FEF0EF')
        canvas.create_window((0, 0), window=scrollable_inner_frame, anchor=tk.NW)

        # Fake review data (replace with actual review data)
        review_data = fetch_reviews()

        for review in review_data:
            review_frame = tk.Frame(scrollable_inner_frame, bg='#FEF0EF')
            review_frame.pack(pady=20)

            stars_label = tk.Label(review_frame, text=f"Stars: {review['stars']}", font=("Arial", 20),
                                   bg='#FEF0EF', fg='black')
            stars_label.pack(pady=5, padx=20)

            user_label = tk.Label(review_frame, text=f"User: {review['user']}", font=("Arial", 20),
                                  bg='#FEF0EF', fg='black')
            user_label.pack(padx=20)

            # Display review text
            text_widget = tk.Text(review_frame, wrap=tk.WORD, height=5, width=50, font=("Arial", 20), bg='#FEF0EF', fg='black',
                                  bd=0, highlightthickness=0)
            text_widget.insert(tk.END, review['comment'])  # Insert the comment text
            text_widget.config(state=tk.DISABLED)  # Disable editing
            text_widget.pack(side=tk.LEFT, padx=20)


    def show_wedding_dresses(self):
        """Display boxes for wedding dresses with distinct names, with scrolling enabled."""
        # Clear the current content
        for widget in self.master.winfo_children():
            widget.destroy()

        # Title label for the wedding dresses page

        self.label = tk.Label(self.master, text="Wedding Dresses", font=("Lucida Calligraphy", 48), bg='#FEF0EF', fg='black')
        self.label.pack(pady=20)

        # Retrieve dress data from the dictionary
        dress_data = {
            'LEONIE': '260235696944', 'BRYNLEE': '366054713060', 'RHYA': '765243351243',
            'HARMONIA': '573762794674', 'MEMPHIS': '247304459935', 'DORI': '223401317803',
            'CARMELLA': '734562441382', 'LUXIA': '549306732031', 'RAMONA': '570882701357',
            'ARACELY': '213175329642', 'BELLIMISA': '379570679859', 'MAIA': '716922330344',
            'TATITANA': '997242272963', 'AURORA': '313455989872', 'NEELA': '144691041532',
            'DOLORES': '532619135710', 'JOLENE': '204820886951', 'VARELLA': '669304145861',
            'SERAPHINE': '381006261038', 'IRIS': '828169952218'
        }

        # Create a frame to hold the canvas and scrollbar
        container = tk.Frame(self.master)
        container.pack(fill="both", expand=True)

        # Create a canvas and a scrollbar
        canvas = tk.Canvas(container, bg='#FEF0EF')
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FEF0EF')


        # Configure the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind the frame to the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Define the size of the box and the space between them
        box_size = 230  # Size of the box

        spacing = 48  # Space between the boxes

        # Create boxes with labels for each dress
        for i, (dress_name, upc) in enumerate(dress_data.items()):
            frame = tk.Frame(scrollable_frame, height=box_size, width=box_size, bg='pink', bd=2, relief="groove")
            frame.grid(row=i // 4, column=i % 4, padx=spacing, pady=spacing)
            label = tk.Label(scrollable_frame, text=dress_name, font=("Arial", 18), bg='#FEF0EF', fg='black')
            label.grid(row=i // 4, column=i % 4, sticky="n")

            # Bind click event to dress box, pass the dress_name and upc
            frame.bind("<Button-1>", lambda event, name=dress_name, code=upc: self.on_dress_box_click(name, code))

        # Back Button
        back_button = tk.Button(self.master, text="Back", font=("Lucida Calligraphy", 18), command=self.show_main_page)
        back_button.pack(pady=10)

        # Update the window to reconfigure its size and position
        self.master.geometry("1280x800")

    def on_dress_box_click(self, dress_name, upc):
        dress_details = fetch_dress_details(dress_name)  # This function needs to return price and color as dress_details[1] and dress_details[2]
        if dress_details:
            dress_window = tk.Toplevel(self.master)
            dress_window.title(dress_name)
            dress_window.geometry("1280x1920")
            dress_window.configure(bg='#FEF0EF')

            tk.Label(dress_window, text=dress_name, font=("Arial", 24)).pack(pady=(10, 0))
            
            # Load and resize the image
            try:
                image_path = f"media/{dress_name}.png"
                pil_image = Image.open(image_path)
                # Resize image to new width and height, using Image.LANCZOS for high quality
                pil_image = pil_image.resize((250, 250), Image.LANCZOS)  # Adjust dimensions as needed
                photo = ImageTk.PhotoImage(pil_image)
                image_label = tk.Label(dress_window, image=photo)
                image_label.image = photo  # Keep a reference!
                image_label.pack(pady=(10, 0))
            except Exception as e:
                print(f"Failed to load image: {e}")
                tk.Label(dress_window, text="Failed to load image", bg='white', width=50, height=20).pack(pady=(10, 0))
            
            tk.Label(dress_window, text=f"Price: {dress_details[2]}", font=("Lucida Calligraphy", 16)).pack(pady=(10, 0))
            tk.Label(dress_window, text=f"Color: {dress_details[3]}", font=("Lucida Calligraphy", 16)).pack(pady=(10, 0))
            tk.Label(dress_window, text=f"Description: {dress_details[4]}", bg='white', fg='black', width=50, height=10).pack(pady=(10, 0))
            
            checkout_button = tk.Button(dress_window, text="Checkout", command=lambda: self.go_to_checkout(dress_details[0]))
            checkout_button.pack(pady=20)
        else:
            messagebox.showerror("Error", "Dress details not found.")

        
    def show_dress_details(self, dress_name, upc):
        # Fetch the details from your data source
        details = fetch_dress_details(dress_name)
        if details:
            dress_window = tk.Toplevel(self.master)
            dress_window.title(dress_name)
            dress_window.geometry("600x800")  # Adjust size as needed
            dress_window.configure(bg='white')

            # Load and display the image
            image_path = f"{dress_name}.png"  # Assuming the image name matches the dress name
            try:
                photo = PhotoImage(file=image_path)
            except Exception as e:
                print(f"Failed to load image: {e}")
                photo = PhotoImage()  # Fallback to an empty image if the load fails

            image_label = tk.Label(dress_window, image=photo)
            image_label.image = photo  # Keep a reference!
            image_label.pack(pady=20)

            # Display dress details
            tk.Label(dress_window, text=f"Name: {dress_name}", font=("Arial", 16)).pack(pady=10)
            tk.Label(dress_window, text=f"UPC: {upc}", font=("Arial", 16)).pack(pady=10)
            tk.Label(dress_window, text=f"Price: {details[2]}", font=("Arial", 16)).pack(pady=10)
            tk.Label(dress_window, text=f"Color: {details[3]}", font=("Arial", 16)).pack(pady=10)
            tk.Label(dress_window, text=f"Description: {details[4]}", font=("Arial", 16)).pack(pady=10)

            # Optionally add a 'Close' button
            close_btn = tk.Button(dress_window, text="Close", command=dress_window.destroy)
            close_btn.pack(pady=20)

    def go_to_checkout(self, upc):
        # Placeholder function to navigate to checkout page
        print("Navigating to checkout page")
        checkout_window = tk.Toplevel(self.master)
        checkout_window.geometry("800x600")
        checkout_window.title("Checkout")
        # checkout_page = CheckoutPage(checkout_window, "user1")
        checkout_page = CheckoutPage(checkout_window, self.username, upc)

    def show_collections(self):
        # Clear the current content if necessary
        for widget in self.master.winfo_children():
            widget.destroy()

        self.label = tk.Label(self.master, text="Collections", font=("Lucida Calligraphy", 48), bg='#FEF0EF', fg='black')
        self.label.pack(pady=20)

        # Frame for collections
        collections_frame = tk.Frame(self.master, bg='#FEF0EF')
        collections_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Box 1 for Collection 1
        box1 = tk.LabelFrame(collections_frame, text="Eternal Whisper", font=("Brush Script MT", 24), bg='white',
                            fg='black', labelanchor='n', width=500, height=300)
        box1.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        box1.pack_propagate(False)
        info1 = tk.Label(box1, text="Classic and timeless bridal gowns.", bg='white', fg='black', font=("Lucida Calligraphy", 25))
        info1.pack(expand=True)
        box1.bind("<Button-1>", lambda e: self.show_collection_dresses(0))  # Show the first 10 dresses

        # Box 2 for Collection 2
        box2 = tk.LabelFrame(collections_frame, text="Celestial Bloom", font=("Brush Script MT", 24), bg='white',
                            fg='black', labelanchor='n', width=500, height=300)
        box2.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        box2.pack_propagate(False)
        info2 = tk.Label(box2, text="Modern designs with a touch of the stars.", bg='white', fg='black',
                        font=("Lucida Calligraphy", 25))
        info2.pack(expand=True)
        box2.bind("<Button-1>", lambda e: self.show_collection_dresses(10))  # Show the last 10 dresses

        # Back Button
        back_button = tk.Button(self.master, text="Back", font=("Lucida Calligraphy", 18), command=self.show_main_page)
        back_button.pack(pady=10)

        # Update the window to reconfigure its size and position
        self.master.geometry("1280x800")  # Resize window back to the main app size




    def show_collection_dresses(self, start_index):
        collection_window = tk.Toplevel(self.master)
        collection_window.title("Collection Dresses")
        collection_window.geometry("1280x1920")
        collection_window.configure(bg='white')

        dress_data = {
            'LEONIE': '260235696944', 'BRYNLEE': '366054713060', 'RHYA': '765243351243',
            'HARMONIA': '573762794674', 'MEMPHIS': '247304459935', 'DORI': '223401317803',
            'CARMELLA': '734562441382', 'LUXIA': '549306732031', 'RAMONA': '570882701357',
            'ARACELY': '213175329642', 'BELLIMISA': '379570679859', 'MAIA': '716922330344',
            'TATITANA': '997242272963', 'AURORA': '313455989872', 'NEELA': '144691041532',
            'DOLORES': '532619135710', 'JOLENE': '204820886951', 'VARELLA': '669304145861',
            'SERAPHINE': '381006261038', 'IRIS': '828169952218'
        }

        # Determine which dresses to display based on start_index
        if start_index == 0:
            displayed_dresses = list(dress_data.items())[:10]
        else:
            displayed_dresses = list(dress_data.items())[10:20]

        # The container frame for the canvas and scrollbar
        container = tk.Frame(collection_window)
        container.pack(fill="both", expand=True)

        # The canvas where we'll draw the dress boxes
        canvas = tk.Canvas(container, bg='#FEF0EF')
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Binding the scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame to pack inside the canvas (this will contain our dress labels)
        scrollable_frame = tk.Frame(canvas, bg='#FEF0EF')

        # Adding the frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Binding the frame to the canvas's scrollregion
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Define size and padding
        box_size = 400
        padding = 50

        # Create labels for each dress within the collection
        for i, (dress_name, upc) in enumerate(displayed_dresses):
            # You could also add images and other details similarly
            frame = tk.Frame(scrollable_frame, height=box_size, width=box_size, bg='pink', bd=2, relief="groove")
            frame.grid(row=i // 5, column=i % 5, padx=padding, pady=padding)
            label = tk.Label(frame, text=dress_name, font=("Arial", 18), bg='pink')
            label.pack(padx=padding, pady=padding)

             # Bind click event to dress box, pass the dress_name and upc
            frame.bind("<Button-1>", lambda event, name=dress_name, code=upc: self.on_dress_box_click(name, code))
            
        back_button = tk.Button(collection_window, text="Back", command=collection_window.destroy)
        back_button.pack(pady=20)


    def setup_homepage(self):
        # Clear existing content
        for widget in self.master.winfo_children():
            widget.destroy()

        # Add components for the home page
        welcome_label = tk.Label(self.master, text="Welcome to Our Bridal Boutique!",

                                 font=("Lucida Calligraphy", 36), bg='#FEF0EF', fg='black')
        welcome_label.pack(pady=20)

        login_button = tk.Button(self.master, text="Login", command=self.open_login, width=20, height=4,
                                 bg="black", fg="white", font=("Lucida Calligraphy", 36))
        login_button.pack(pady=10)

        # More components like registration, info, etc.

    def setup_main_ui(self):
        """Sets up or resets the main UI components to their original state."""
        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        self.master.title("Main Page")
        self.master.geometry("1280x1920")
        self.master.configure(bg='#FEF0EF')  # Cream background

        self.label = tk.Label(self.master, text="H.E.M.", font=("Lucida Calligraphy", 48), bg='#FEF0EF', fg='black')
        self.label.pack(pady=20)

        # Set background color for the menu bar
        menu_bg_color = self.master.cget("bg")

        # Create a frame to hold the menu bar
        menu_frame = tk.Frame(self.master, bg=menu_bg_color)  # Add border and relief
        menu_frame.pack(side=tk.TOP, pady=10)

        # Create a dropdown button for the account
        self.account_menu = tk.Menubutton(menu_frame, text="Account", compound=tk.LEFT, bg=menu_bg_color, fg='black',
                                          font=("Brush Script MT", 18))
        self.account_menu.menu = tk.Menu(self.account_menu, tearoff=0)
        self.account_menu["menu"] = self.account_menu.menu

        # Add options to the account menu
        self.account_menu.menu.add_command(label="Profile", command=self.show_profile)
        self.account_menu.menu.add_command(label="Logout", command=self.logout)

        self.account_menu.pack(side=tk.RIGHT, padx=10)
        # Configure button style to remove button shape
        button_style = {"border": 1, "bg": menu_bg_color, "width": 13, "height": 2, "highlightbackground": "black",
                        "relief": "solid", "fg":"black"}

        buttons_data = [
            ("Wedding Dresses",
             self.show_wedding_dresses),
            ("Collections", self.show_collections),
            ("Styles", self.show_styles),
            ("Reviews", self.show_reviews)
        ]

        # Create menu buttons
        for text, command in buttons_data:
            button = tk.Button(menu_frame, text=text, font=("Brush Script MT", 24),
                               command=command, **button_style)
            button.pack(side=tk.LEFT, padx=10)

        # Center the menu bar horizontally
        menu_frame.place(relx=.5, rely=.15, anchor=tk.CENTER)

        # Create a frame to hold the photo boxes
        photo_frame = tk.Frame(self.master, bg='#FEF0EF')
        photo_frame.pack(pady=20)
        photo_frame.place(relx=0.5, rely=0.58, anchor=tk.CENTER)

        # Placeholder images, replace with actual photo paths
        image_paths = ["media/VARELLA.png", "media/ARACELY.png"]

        for image_path in image_paths:
            img = Image.open(image_path)
            img = img.resize((400, 400))  # Resize the image
            photo = ImageTk.PhotoImage(img)

            # Create photo box
            photo_box = tk.Label(photo_frame, image=photo)
            photo_box.image = photo  # Store reference to prevent garbage collection
            photo_box.pack(side=tk.LEFT, padx=40)

        self.footer = create_footer(self.master)

        # Create a frame for reviews
        self.reviews_frame = tk.Frame(self.master, bg='#FEF0EF')
        self.reviews_frame.pack(pady=20)

    def show_main_page(self):
        """Shows the main page by resetting UI to its initial state."""
        self.setup_main_ui()  # Re-setup the UI

    def show_styles(self):
        """Display style options with four distinct categories."""
        # Clear the current content
        for widget in self.master.winfo_children():
            widget.destroy()

        # Title label for the styles page
        self.label = tk.Label(self.master, text="Choose Your Style", font=("Lucida Calligraphy", 48), bg='#FEF0EF', fg='black')
        self.label.pack(pady=20)

        # Frame for styles
        styles_frame = tk.Frame(self.master, bg='#FEF0EF')
        styles_frame.pack(expand=True, fill="both", pady=20)

        # Data for each style box
        styles_data = [
            ("Elegant", self.elegant_dresses),
            ("Boho", self.boho_dresses),
            ("Vintage", self.vintage_dresses),
            ("Princess", self.princess_dresses)
        ]

        # Create style boxes
        for style, dresses in styles_data:
            button = tk.Button(styles_frame, text=style, font=("Brush Script MT", 24), bg='white', fg='black',
                            command=lambda d=dresses: self.display_style_dresses(d, style))
            button.pack(side="left", padx=10, pady=10, expand=True)

        # Back Button
        back_button = tk.Button(self.master, text="Back", font=("Lucida Calligraphy", 18), command=self.show_main_page)
        back_button.pack(pady=10)



    def display_style_dresses(self, dresses, style_name):
        """Display dresses for the selected style in a new window with clickable boxes."""
        dress_window = tk.Toplevel(self.master)
        dress_window.title(f"{style_name} Dresses")
        dress_window.geometry("1280x1920")
        dress_window.configure(bg='#FEF0EF')

        tk.Label(dress_window, text=f"{style_name} Style Dresses", font=("Lucida Calligraphy", 36), bg='#FEF0EF').pack(pady=20)

        container = tk.Frame(dress_window)
        container.pack(fill="both", expand=True)

        # Horizontal layout
        scrollable_frame = tk.Frame(container, bg='#FEF0EF')
        scrollable_frame.pack(fill="both", expand=True)

        for dress in dresses:
            upc = self.dress_data.get(dress, "Unknown UPC")  # Get UPC or default to 'Unknown UPC'
            # Creating larger frames for each dress
            frame = tk.Frame(scrollable_frame, height=300, width=300, bg='pink', bd=2, relief="groove")
            frame.pack(side="left", padx=20, pady=10, expand=True)
            label = tk.Label(frame, text=dress, font=("Arial", 20), bg='pink')
            label.pack(expand=True, fill="both")
            label.bind("<Button-1>", lambda event, d=dress, u=upc: self.on_dress_box_click(d, u))

        back_button = tk.Button(dress_window, text="Back", font=("Lucida Calligraphy", 18), command=dress_window.destroy)
        back_button.pack(pady=20)



    def show_profile(self):
        print("Showing Profile Page")
        # Use self.username to access the username
        root = tk.Toplevel()
        app = ProfilePage(root, self.username)
        root.mainloop()

    def logout(self):
        print("You logged out successfully.")
        self.master.destroy()
        root = tk.Toplevel()
        app = HomePage(root)
        root.mainloop()

class UploadPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Upload Wedding Dresses")
        self.master.geometry("800x800")
        self.master.configure(bg='#FDE1DE')  # Cream background

        self.label = tk.Label(master, text="Upload Wedding Dresses", font=("Lucida Calligraphy", 24), bg='#FDE1DE',
                              fg='black')
        self.label.pack(pady=20)

        # Create button to trigger upload
        self.upload_button = tk.Button(master, text="Upload Dresses", command=self.open_dress_info_window,
                                       bg='white', fg='black',
                                       font=("Lucida Calligraphy", 18), width=25, height=4,
                                       bd=1, relief="solid", highlightbackground="black")
        self.upload_button.pack(pady=10)

        # Create button to open window for updating wedding dress table
        self.update_button = tk.Button(master, text="Update Wedding Dresses", command=self.open_update_window,
                                       bg='white', fg='black',
                                       font=("Lucida Calligraphy", 18), width=25, height=4,
                                       bd=1, relief="solid", highlightbackground="black")
        self.update_button.pack(pady=10)

        # Create button to add new dress
        self.add_button = tk.Button(master, text="Add Dress", command=self.open_add_window, bg='white', fg='black',
                                    font=("Lucida Calligraphy", 18), width=25, height=4,
                                    bd=1, relief="solid", highlightbackground="black")
        self.add_button.pack(pady=10)

        # Create button to delete dress
        self.delete_button = tk.Button(master, text="Delete Dress", command=self.open_delete_window,
                                       bg='white', fg='black',
                                       font=("Lucida Calligraphy", 18), width=25, height=4,
                                       bd=1, relief="solid", highlightbackground="black")
        self.delete_button.pack(pady=10)

    def open_dress_info_window(self):
        # Create a new window for dress information
        dress_info_window = tk.Toplevel(self.master)
        dress_info_window.title("Dress Info Employee")

        # Create a treeview to display the dress info in a table
        tree = ttk.Treeview(dress_info_window)
        tree["columns"] = (
            "UPC", "Name", "Price", "Color", "Description", "Elegant", "Vintage", "Princess", "Boho", "C1", "C2")
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        # Fetch dress info as dictionaries
        dress_info = fetch_dress_info_employee()
        for i, dress in enumerate(dress_info, start=1):
            tree.insert("", "end", text=str(i), values=list(dress.values()))

        # Adjust column widths based on content
        for col in tree["columns"]:
            tree.heading(col, text=col, command=lambda _col=col: self.sort_column(tree, _col, False))
            max_width = max(len(tree.set(child, col)) for child in tree.get_children())
            tree.column(col, width=max_width * 10)  # Adjust the multiplier as needed

        tree.pack(expand=True, fill=tk.BOTH)

    def open_update_window(self):
        # Create new window for updating dress info
        update_window = tk.Toplevel(self.master)
        update_window.title("Update Wedding Dress")
        update_window.geometry("600x600")
        update_window.configure(bg='#FDE1DE')

        labels = ["UPC", "Name", "Price", "Color", "Description", "Elegant", "Vintage", "Princess", "Boho", "C1", "C2"]
        self.entries = []

        # Create entry boxes associated with labels in two columns
        for i, label_text in enumerate(labels):
            row = i // 2  # Calculate row index
            column = i % 2  # Calculate column index
            label = tk.Label(update_window, text=label_text, font=("Arial", 12), bg='#FDE1DE', fg='black')
            label.grid(row=row, column=column * 2, padx=5, pady=5)
            entry = tk.Entry(update_window, font=("Arial", 12))
            entry.grid(row=row, column=column * 2 + 1, padx=5, pady=5)
            self.entries.append(entry)
        update_button = tk.Button(update_window, text="Update", command=self.update_dress,
                                  bg='white', fg='black',
                                  font=("Lucida Calligraphy", 16), width=6, height=2,
                                  bd=1, relief="solid", highlightbackground="black"
                                  )
        update_button.grid(row=(len(labels) + 1) // 2, column=0, columnspan=2, pady=20)  # Span across two columns

    def update_dress(self):
        # Get data from entry widgets
        data = [entry.get() for entry in self.entries]

        # Extract specific fields from data
        upc, name, price, color = data[:4]

        # Check if any of the required fields are empty
        if not (upc and name and price and color):
            messagebox.showerror("Error", "Please fill in all required fields (UPC, Name, Price, Color)")
            return
        # Print the data for debugging
        print("Data to be updated:", data)

        # Call the updatedress function with extracted data
        success = updatedress(*data)

        #Check if the update was successful
        if success:
            messagebox.showinfo("Success", "Dress updated successfully")
        else:
            messagebox.showerror("Error", "Failed to update dress")

    def open_add_window(self):
        # Create new window for updating dress info
        update_window = tk.Toplevel(self.master)
        update_window.title("Add Wedding Dress")
        update_window.geometry("600x600")
        update_window.configure(bg='#FDE1DE')

        labels = ["UPC", "Name", "Price", "Color", "Description", "Elegant", "Vintage", "Princess", "Boho", "C1", "C2"]
        self.entries = []

        # Create entry boxes associated with labels in two columns
        for i, label_text in enumerate(labels):
            row = i // 2  # Calculate row index
            column = i % 2  # Calculate column index
            label = tk.Label(update_window, text=label_text, font=("Arial", 12), bg='#FDE1DE', fg='black')
            label.grid(row=row, column=column * 2, padx=5, pady=5)
            entry = tk.Entry(update_window, font=("Arial", 12))
            entry.grid(row=row, column=column * 2 + 1, padx=5, pady=5)
            self.entries.append(entry)
        update_button = tk.Button(update_window, text="Add", command=self.add_dress,
                                  bg='white', fg='black',
                                  font=("Lucida Calligraphy", 16), width=6, height=2,
                                  bd=1, relief="solid", highlightbackground="black"
                                  )
        update_button.grid(row=(len(labels) + 1) // 2, column=0, columnspan=2, pady=20)  # Span across two columns

    def add_dress(self):
        # Get data from entry widgets
        data = [entry.get() for entry in self.entries]

        # Extract specific fields from data
        upc, name, price, color = data[:4]

        # Check if any of the required fields are empty
        if not (upc and name and price and color):
            messagebox.showerror("Error", "Please fill in all required fields (UPC, Name, Price, Color)")
            return
        # Print the data for debugging
        print("Data to be added:", data)

        # Call the add_wedding_dress function with extracted data
        success = add_wedding_dress(*data)

        #Check if the added was successful
        if success:
            messagebox.showinfo("Success", "Dress added successfully")
        else:
            messagebox.showerror("Error", "Failed to added dress")

    def open_delete_window(self):
        # Create new window for deleting dress
        delete_window = tk.Toplevel(self.master)
        delete_window.title("Delete Wedding Dress")
        delete_window.geometry("300x200")
        delete_window.configure(bg='#FDE1DE')

        # Create label and entry for UPC
        upc_label = tk.Label(delete_window, text="UPC:", font=("Arial", 12), bg='#FDE1DE', fg='black')
        upc_label.pack(pady=10)
        self.upc_entry = tk.Entry(delete_window, font=("Arial", 12))
        self.upc_entry.pack(pady=5)

        # Create button to delete dress
        delete_button = tk.Button(delete_window, text="Delete", command=self.delete_dress, bg='white', fg='black',
                                  font=("Lucida Calligraphy", 16), width=6, height=2,
                                  bd=1, relief="solid", highlightbackground="black"
                                  )
        delete_button.pack(pady=10)

    def delete_dress(self):
        # Get UPC from entry widget
        upc = self.upc_entry.get()

        if not upc:
            messagebox.showerror("Error", "Please fill in all required fields (UPC)")
            return

        success = delete_wedding_dress(upc)

        # Check if the deletion was successful
        if success:
            messagebox.showinfo("Success", "Dress deleted successfully")
        else:
            messagebox.showerror("Error", "Failed to deleted dress")



class EmployeeUpdatePage:
    def __init__(self, master, employee_id):
        self.master = master
        self.employee_id = employee_id

        self.master.title("Employee Update Options")
        self.master.geometry("1280x720")
        self.master.configure(bg='#FDE1DE')  # Cream background

        # Calculate the center position
        center_x = 1280 // 2
        center_y = 720 // 2

        # Create and place the title label
        self.label_title = tk.Label(master, text="Employee Update Options", font=("Lucida Calligraphy", 24, "bold"),
                                    bg='#FDE1DE', fg='black')
        self.label_title.place(relx=0.5, rely=0.1, anchor="center")

        # Create and place the "Update Customer Information" button
        self.button_update_customer = tk.Button(master, text="Update Customer Information",
                                                command=self.update_customer_info, bg='white', fg='black',
                                                font=("Lucida Calligraphy", 18), width=30, height=5,
                                                bd=2, relief="solid", highlightbackground="black")
        self.button_update_customer.place(relx=0.5, rely=0.3, anchor="center")

        # Create and place the "Update Employee Information" button
        self.button_update_employee = tk.Button(master, text="Update Employee Information",
                                                command=self.update_employee_info, bg='white', fg='black',
                                                font=("Lucida Calligraphy", 18), width=30, height=5,
                                                bd=2, relief="solid", highlightbackground="black")
        self.button_update_employee.place(relx=0.5, rely=0.5, anchor="center")

        # Create and place the "Update Wedding Database Information" button
        self.button_update_wedding = tk.Button(master, text="Update Wedding Database Information",
                                               command=self.update_wedding_info, bg='white', fg='black',
                                               font=("Lucida Calligraphy", 18), width=30, height=5,
                                               bd=2, relief="solid", highlightbackground="black")
        self.button_update_wedding.place(relx=0.5, rely=0.7, anchor="center")
        self.footer = create_footer(master)
    
    def update_customer_info(self):
        # Create a pop-up window to ask for the customer's username
        popup = tk.Toplevel(self.master)
        popup.title("Enter Customer Username")
        popup.geometry("400x200")
        popup.configure(bg='#FDE1DE')  # Use the same pink shade as the employee login page

        # Label and Entry for entering the customer's username
        label_username = tk.Label(popup, text="Enter Customer Username:", font=("Lucida Calligraphy", 14), bg='#FDE1DE',
                                fg='black')
        label_username.pack(pady=10)
        entry_username = tk.Entry(popup, bg='white', fg='black', font=("Lucida Calligraphy", 14))
        entry_username.pack(pady=5)

        # Function to handle submitting the username
        def submit_username():
            username = entry_username.get()
            if username:
                popup.destroy()  # Close the pop-up window
                # Proceed to the profile page with the entered username
                root = tk.Toplevel()
                app = ProfilePage(root, username)
                root.mainloop()
            else:
                messagebox.showerror("Error", "Please enter a username.")

        # Button to submit the username
        submit_button = tk.Button(popup, text="Submit", command=submit_username, bg='white', fg='black',
                                font=("Lucida Calligraphy", 14))
        submit_button.pack(pady=10)

        # Keep the pop-up window open until closed
        popup.mainloop()
        
    def update_employee_info(self):
        # Placeholder function to navigate to update employee information page
        print("Navigate to update employee information page")
        root = tk.Toplevel()
        app = UpdateEmployeeInfoPage(root, self.employee_id)
        root.mainloop()


    def update_wedding_info(self):
        root = tk.Toplevel()  # Create a new Tkinter root window for the main page
        app = UploadPage(root)  # Open the choose to edit account or database
        root.mainloop()

class UpdateEmployeeInfoPage:
    def __init__(self, master, employee_id):
        self.master = master
        self.master.title("Update Employee Information")
        self.master.geometry("1280x800")  # Adjusted height for better visibility
        self.master.configure(bg='#FDE1DE')  # Cream background

        # Fetch employee data from the database
        self.employee_data = fetch_employee_data(employee_id)

        if self.employee_data:
            # Display employee name in a bigger font at the top center
            name_label = tk.Label(master, text=f"{self.employee_data['first_name']} {self.employee_data['last_name']}",
                                  font=("Lucida Calligraphy", 36), bg='#FDE1DE', fg='black')
            name_label.pack(pady=20)

            # Display employee username
            username_label = tk.Label(master, text=f"Username: {self.employee_data['username']}",
                                      font=("Brush Script MT", 20), bg='#FDE1DE', fg='black')
            username_label.pack()

            # Display employee ID
            employee_id_label = tk.Label(master, text=f"Employee ID: {self.employee_data['employee_id']}",
                                         font=("Brush Script MT", 20), bg='#FDE1DE', fg='black')
            employee_id_label.pack()

            # Adding a line for separation
            separator1 = tk.Frame(master, height=2, bd=1, relief="groove", bg='black')
            separator1.pack(fill="x", padx=20, pady=10)

            row = 3
            # Display the rest of the information in the middle of the page
            self.entry_fields = {}
            self.labels = {}
            fields_to_update = ["email", "phone_number", "address"]
            for field in fields_to_update:
                label = tk.Label(master, text=f"{field.replace('_', ' ').title()}: ", font=("Brush Script MT", 16),
                                 bg='#FDE1DE', fg='black')
                label.place(x=640 - 150, y=150 + row * 30, anchor="e")
                self.labels[field] = label

                entry = tk.Entry(master, font=("Arial", 12), bg='white', fg='black')
                entry.insert(0, self.employee_data.get(field, ""))  # Insert data if available, else empty string
                entry.place(x=640 - 100, y=150 + row * 30, anchor="w")
                self.entry_fields[field] = entry

                update_button = tk.Button(master, text="Update", command=lambda k=field: self.update_field(k),
                                          bg='#FDE1DE', fg='black', font=("Lucida Calligraphy", 14))
                update_button.place(x=640 + 100, y=150 + row * 30, anchor="w")

                row += 1

        else:
            # Display message if employee data is not found
            error_label = tk.Label(master, text="Employee data not found", font=("Arial", 20), bg='#FDE1DE', fg='red')
            error_label.pack(pady=20)

    def update_field(self, field):
        entry = self.entry_fields[field]  # Retrieve the entry field associated with the updated value
        new_value = entry.get()
        update_employee_data(self.employee_data['employee_id'], field, new_value)
        self.employee_data[field] = new_value
        self.labels[field].config(text=f"{field.replace('_', ' ').title()}: {new_value}")


def verify_password(password):
    # At least 8 characters
    if len(password) < 8:
        return False

    # At least one uppercase letter
    if not any(char.isupper() for char in password):
        return False

    # At least one special character
    if not any(char in string.punctuation for char in password):
        return False

    # At least one number
    if not any(char.isdigit() for char in password):
        return False

    return True

class CustomerLoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Login / Sign Up")
        self.master.geometry("1280x720")  # Adjusted height for better visibility
        self.master.configure(bg='#FDE1DE')  # Cream background

        # Add a frame to contain all the login elements
        self.frame = tk.Frame(master, bg='#FDE1DE')
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create and place the "Login" label
        self.label_login = tk.Label(self.frame, text="Login", font=("Lucida Calligraphy", 24, "bold"), bg='#FDE1DE',
                                    fg='black')
        self.label_login.pack(pady=(20, 10))

        # Create and place the "Username" label and entry
        self.label_username = tk.Label(self.frame, text="Username:", font=("Lucida Calligraphy", 16), bg='#FDE1DE',
                                       fg='black')
        self.label_username.pack()
        self.entry_username = tk.Entry(self.frame, bg='white', fg='black', font=("Lucida Calligraphy", 16))
        self.entry_username.pack()

        # Create and place the "Password" label and entry
        self.label_password = tk.Label(self.frame, text="Password:", font=("Lucida Calligraphy", 16), bg='#FDE1DE',
                                       fg='black')
        self.label_password.pack()
        self.entry_password = tk.Entry(self.frame, show="*", bg='white', fg='black', font=("Lucida Calligraphy", 16))
        self.entry_password.pack()

        # Create and place the "Login" button
        self.login_button = tk.Button(self.frame, text="Login", command=self.login, bg='white', fg='black',
                                      font=("Lucida Calligraphy", 16))
        self.login_button.pack(pady=10)

        # Create and place the "Sign Up" label
        self.label_signup = tk.Label(self.frame, text="Sign Up", font=("Lucida Calligraphy", 24, "bold"), bg='#FDE1DE',
                                     fg='black')
        self.label_signup.pack(pady=(20, 10))

        # Create and place the "New Username" label and entry
        self.label_new_username = tk.Label(self.frame, text="New Username:", font=("Lucida Calligraphy", 16),
                                           bg='#FDE1DE', fg='black')
        self.label_new_username.pack()
        self.entry_new_username = tk.Entry(self.frame, bg='white', fg='black', font=("Lucida Calligraphy", 16))
        self.entry_new_username.pack()

        # Create and place the "New Password" label and entry
        self.label_new_password = tk.Label(self.frame, text="New Password:", font=("Lucida Calligraphy", 16),
                                           bg='#FDE1DE', fg='black')
        self.label_new_password.pack()
        self.entry_new_password = tk.Entry(self.frame, show="*", bg='white', fg='black', font=("Lucida Calligraphy", 16))
        self.entry_new_password.pack()

        # Create and place the "First Name" label and entry
        self.label_firstname = tk.Label(self.frame, text="First Name:", font=("Lucida Calligraphy", 16),
                                         bg='#FDE1DE', fg='black')
        self.label_firstname.pack()
        self.entry_firstname = tk.Entry(self.frame, bg='white', fg='black', font=("Lucida Calligraphy", 16))
        self.entry_firstname.pack()

        # Create and place the "Last Name" label and entry
        self.label_lastname = tk.Label(self.frame, text="Last Name:", font=("Lucida Calligraphy", 16),
                                        bg='#FDE1DE', fg='black')
        self.label_lastname.pack()
        self.entry_lastname = tk.Entry(self.frame, bg='white', fg='black', font=("Lucida Calligraphy", 16))
        self.entry_lastname.pack()

        # Create and place the "Sign Up" button
        self.signup_button = tk.Button(self.frame, text="Sign Up", command=self.signup, bg='white', fg='black',
                                       font=("Lucida Calligraphy", 16))
        self.signup_button.pack(pady=10)

        # Error message label
        self.message = tk.Label(self.frame, text="", fg="red", bg='#FDE1DE')
        self.message.pack()
        
    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        # Placeholder authentication logic
        if u_check_login(username, password):
            self.master.destroy()  # Close the login window
            root = tk.Toplevel()  # Create a new Tkinter root window for the main page
            app = MainPage(root, username)  # Pass username to MainPage
            root.mainloop()  # Show the homepage
        else:
            self.message.config(text="Invalid username or password")

    def signup(self):
        # Reset the error message label
        self.message.config(text="")
        new_username = self.entry_new_username.get()
        new_password = self.entry_new_password.get()
        firstname = self.entry_firstname.get()
        lastname = self.entry_lastname.get()

        # Verify password
        if not verify_password(new_password):
            self.message.config(text="Password does not meet the requirements.")
        elif not new_username or not new_password:
            self.message.config(text="Please enter both username and password.")
        else:
            if create_user(new_username, new_password, firstname, lastname, "", "", ""):
                self.message.config(text="Sign up successful!")
                self.master.destroy()  # Close the login window
                root = tk.Toplevel()  # Create a new Tkinter root window for the main page
                app = MainPage(root, new_username)  # Open the main page
                root.mainloop()
            else:
                self.message.config(text="Failed to sign up. Please try again.")



class EmployeeLoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("1280x1920")
        self.master.configure(bg='#FDE1DE')  # Cream background

        # Calculate the center position
        center_x = 1280 // 2
        center_y = 1920 // 2

        # Create and place the "Login" label
        self.label_login = tk.Label(master, text="Login", font=("Lucida Calligraphy", 36, "bold"), bg='#FDE1DE',
                                    fg='black')
        self.label_login.place(relx=0.5, rely=0.2, anchor="center")

        # Create and place the "Employee ID" label and entry
        self.label_employee_id = tk.Label(master, text="Employee ID:", font=("Lucida Calligraphy", 20), bg='#FDE1DE',
                                          fg='black')
        self.label_employee_id.place(relx=0.3, rely=0.3, anchor="center")
        self.entry_employee_id = tk.Entry(master, bg='white', fg='black', font=("Lucida Calligraphy", 20),
                                          highlightthickness=0)
        self.entry_employee_id.place(relx=0.5, rely=0.3, anchor="center")

        # Create and place the "Username" label and entry
        self.label_username = tk.Label(master, text="Username:", font=("Lucida Calligraphy", 20), bg='#FDE1DE',
                                       fg='black')
        self.label_username.place(relx=0.3, rely=0.4, anchor="center")
        self.entry_username = tk.Entry(master, bg='white', fg='black', font=("Lucida Calligraphy", 20),
                                       highlightthickness=0)
        self.entry_username.place(relx=0.5, rely=0.4, anchor="center")

        # Create and place the "Password" label and entry
        self.label_password = tk.Label(master, text="Password:", font=("Lucida Calligraphy", 20), bg='#FDE1DE',
                                       fg='black')
        self.label_password.place(relx=0.3, rely=0.5, anchor="center")
        self.entry_password = tk.Entry(master, show="*", bg='white', fg='black', font=("Lucida Calligraphy", 20),
                                       highlightthickness=0)
        self.entry_password.place(relx=0.5, rely=0.5, anchor="center")

        # Create and place the "Login" button
        self.login_button = tk.Button(master, text="Login", command=self.login, bg='white', fg='black',
                                      font=("Lucida Calligraphy", 20), height=2, width=7)
        self.login_button.place(relx=0.5, rely=0.6, anchor="center")
        self.footer = create_footer(master)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        employee_id = self.entry_employee_id.get()

        # Placeholder authentication logic
        # Replace this with your actual authentication logic
        if e_check_login(employee_id, username, password):
            self.master.destroy()  # Close the login window
            root = tk.Toplevel()  # Create a new Tkinter root window for the main page
            app = EmployeeUpdatePage(root, employee_id)  # Open the choose to edit account or database

            root.mainloop()  # Show the homepage
        else:
            self.message.config(text="Invalid employee ID, username, or password")


class LoginDecide:
    def __init__(self, master, homepage):
        self.master = master
        self.master.title("Login Decision")
        self.master.geometry("1280x1920")
        self.homepage = homepage
        self.master.configure(bg='#E4B1AB')  # Cream background
        self.label = tk.Label(master, text="Customer or Employee", font=("Brush Script MT", 48), bg='#E4B1AB',
                              fg='black')
        self.label.pack(pady=(50, 20))

        login_frame = tk.Frame(master, pady=20, bg='#E4B1AB')
        login_frame.pack(pady=50)

        customer_login_button = tk.Button(login_frame, text="Login as Customer", command=self.login_customer, height=7,
                                          width=20, font=("Lucida Calligraphy", 24))
        customer_login_button.grid(row=0, column=0, padx=50, pady=20, ipadx=50)

        employee_btn = tk.Button(login_frame, text="Login as Employee", command=self.login_employee, height=7, width=20,
                                 font=("Lucida Calligraphy", 24))
        employee_btn.grid(row=0, column=1, padx=50, pady=20, ipadx=50)

        self.footer = create_footer(master)

    def login_customer(self):
        self.master.destroy()
        root = tk.Toplevel()  # Create a new Tkinter root window for the main page
        app = CustomerLoginPage(root)  # Open the main page
        root.mainloop()  # Show the homepage

    def login_employee(self):
        self.master.destroy()
        root = tk.Toplevel()  # Create a new Tkinter root window for the main page
        app = EmployeeLoginPage(root)  # Open the main page
        root.mainloop()  # Show the homepage


class HomePage:
    def __init__(self, master):
        self.master = master
        self.master.title("Bridal Website")
        self.master.geometry("1280x1920")
        self.master.configure(bg='black')  # Cream background

        # Load the background image
        self.background_image = Image.open("home-image.png")
        self.background_image = self.background_image.resize((1200, 800))
        self.photo = ImageTk.PhotoImage(self.background_image)

        # Create a label to hold the background image
        background_label = tk.Label(master, image=self.photo, bg="black", width=1280, height=1920)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Ensure that the image is not garbage collected
        background_label.image = self.background_image

        self.label = tk.Label(master, text="H.E.M.", font=("Lucida Calligraphy", 48), bg='#E4B1AB', fg='black', pady=10,

                              padx=15, bd=2, relief="solid", highlightbackground="black")
        self.label.pack(pady=20)

        # Split the message into three lines
        message_line1 = "Unlock Your Dream Bridal Experience!"
        message_line2 = "Click the Login button to embark on your journey"
        message_line3 = "to finding the perfect dress and creating unforgettable memories!"

        font_style = ("Brush Script MT", 28)
        # Create a black frame behind the text labels
        self.message_frame = tk.Frame(master, bg='#E4B1AB', pady=10, padx=20, bd=2, relief="solid",
                                      highlightbackground="black")
        self.message_frame.pack(pady=20)

        self.label_message_line1 = tk.Label(self.message_frame, text=message_line1, font=font_style, bg='#E4B1AB',
                                            fg='black')
        self.label_message_line1.pack(pady=5)

        self.label_message_line2 = tk.Label(self.message_frame, text=message_line2, font=font_style, bg='#E4B1AB',
                                            fg='black')
        self.label_message_line2.pack(pady=5)

        self.label_message_line3 = tk.Label(self.message_frame, text=message_line3, font=font_style, bg='#E4B1AB',
                                            fg='black')
        self.label_message_line3.pack(pady=5)

        self.login_button = tk.Button(master, text="Login", command=self.open_login, width=10, height=2,
                                      bg="#E4B1AB", fg="black", font=("Lucida Calligraphy", 36),
                                      bd=1.3, relief="solid", highlightbackground="black")
        self.login_button.pack(pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=master.destroy, width=10, height=2,
                                     bg="#E4B1AB", fg="black", font=("Lucida Calligraphy", 36),
                                     bd=1.3, relief="solid", highlightbackground="black")
        self.exit_button.pack(pady=10)

        self.footer = create_footer(master)

    def open_login(self):
        # Add code to open the login window
        self.master.iconify()  # Minimize the homepage window
        login_window = tk.Toplevel()
        LoginDecide(login_window, self)
        pass


def main():
    root = tk.Tk()
    app = HomePage(root)
    root.mainloop()


if __name__ == "__main__":
    main()

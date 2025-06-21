import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import requests

class OSINTApp:
    """
    A simple OSINT (Open Source Intelligence) application with GUI using Tkinter.
    The program will feature API's to pull website placement 
    """
    def __init__(self, master):
        """
        Initializes the OSINT App.
        Args:
            master: The root Tkinter window (or parent widget).
        """
        self.master = master
        self.master.title("Custom OSINT Tool")
        self.master.geometry('960x720')
        self.master.configure(bg="#fffdca") # Background color

        # Configure grid weights for responsive layout
        # This makes the columns and rows expand proportionally when the window is resized.
        self.master.grid_rowconfigure(0, weight=0) # Title
        self.master.grid_rowconfigure(1, weight=0) # Developer info
        self.master.grid_rowconfigure(2, weight=0) # Input frame (adjust as needed)
        self.master.grid_rowconfigure(3, weight=1) # Results frame (this will expand)
        self.master.grid_rowconfigure(4, weight=0) # Status bar

        self.master.grid_columnconfigure(0, weight=1) # Make the main column expandable

        self._create_widgets()

    def _create_widgets(self):
        # --- Title and Developer Info ---
        tk.Label(self.master, text="Custom OSINT Tool", bg="#fffdca", font=("Times New Roman", 16, "bold")).grid(
            row=0, column=0, pady=(10, 0), sticky="n" # Centered at the top
        )
        tk.Label(self.master, text="This tool was developed by Tristan Hatfield, Petra Kelly, Bryan Bachleda, Adam Lazarowicz", bg="#fffdca").grid(
            row=1, column=0, pady=(0, 10), sticky="n" # Below the title
        )

        # --- Input Frame ---
        # This frame will hold the link entries for the APIs and the Analyze button.
        input_frame = ttk.LabelFrame(self.master, text="Analysis", padding="10 10 10 10")
        input_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1) # Allow the entry field to expand

        tk.Label(input_frame, text="Enter the Business's Website Link:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.yelp_entry = ttk.Entry(input_frame, width=60) # Use ttk.Entry for modern look
        self.yelp_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.yelp_entry.bind("<Return>", lambda event: self._analyze_data()) # Bind Enter key to analysis

        analyze_button = ttk.Button(input_frame, text="Analyze Data", command=self._analyze_data(yelp_entry))
        analyze_button.grid(row=1, column=0, columnspan=2, pady=10) # Span across both columns

        # --- Results Display Frame ---
        # This frame will contain the scrolled text area for displaying results.
        results_frame = ttk.LabelFrame(self.master, text="Analysis Results", padding="10 10 10 10")
        results_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1) # Make the text area expand vertically
        results_frame.grid_columnconfigure(0, weight=1) # Make the text area expand horizontally

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=80, height=15, font=("Consolas", 10))
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_text.insert(tk.END, "Enter a relevant links and click 'Analyze Data' to see results.\n")
        self.results_text.config(state=tk.DISABLED) # Make text area read-only initially

        # Clear Results Button
        clear_button = ttk.Button(results_frame, text="Clear Results", command=self._clear_results)
        clear_button.grid(row=1, column=0, pady=(10, 0)) # Below the text area

        # --- Status Bar ---
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=4, column=0, sticky="ew", padx=20, pady=(5, 10))



def _analyze_data(self, yelp_url):    
    url = "https://yelp-business-api.p.rapidapi.com/reviews"
    
    querystring = {"business_url":yelp_url,"reviews_per_page":"10","sort_by":"Yelp_sort","rating_filter":"All_ratings"}
    
    headers = {
    	"x-rapidapi-key": "24487241e5msh7d9e4ee01600512p1b9d7ejsn6b28ebd02ccf",
    	"x-rapidapi-host": "yelp-business-api.p.rapidapi.com"
    }
    
    yelp_response = requests.get(url, headers=headers, params=querystring)
    text += yelp_response.json()

    
    
    

    def _append_to_results(self, text):
        """
        Appends text to the results display area.
        Ensures the text area is writable before appending and then set back to read-only.
        """
        self.results_text.config(state=tk.NORMAL) # Enable editing
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END) # Scroll to the end
        self.results_text.config(state=tk.DISABLED) # Disable editing

    def _clear_results(self):
        """
        Clears all text from the results display area.
        """
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Results cleared. Ready for new analysis.\n")
        self.results_text.config(state=tk.DISABLED)
        self.status_bar.config(text="Ready")
        self.yelp_entry.delete(0, tk.END) # Also clear the input field

# Main execution block
if __name__ == "__main__":
    root = tk.Tk()
    app = OSINTApp(root)
    root.mainloop()

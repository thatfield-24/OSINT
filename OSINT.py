import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog

class OSINTApp:
    """
    A simple OSINT (Open Source Intelligence) application with GUI using Tkinter.
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

        tk.Label(input_frame, text="Enter the Facebook link:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fb_entry = ttk.Entry(input_frame, width=60) # Use ttk.Entry for modern look
        self.fb_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.fb_entry.bind("<Return>", lambda event: self._analyze_data()) # Bind Enter key to analysis

        analyze_button = ttk.Button(input_frame, text="Analyze Data", command=self._analyze_data)
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

    def _analyze_data(self):
        """
        This is where API logic will go.
        """
        facebook_link = self.fb_entry.get().strip() # Removes any accidental whitespace characters

        if not facebook_link:
            messagebox.showwarning("Input Error", "Please enter a Facebook link to analyze.")
            self.status_bar.config(text="Error: No link entered.")
            return

        self.status_bar.config(text=f"Analyzing: {facebook_link}...")
        self._append_to_results(f"\n--- Analyzing Facebook Link: {facebook_link} ---\n")

        # --- OSINT LOGIC ---
        # Replace this section with OSINT functions.
        try:

            if "facebook.com/" in facebook_link:
                simulated_output = f"""
                [Simulated Analysis Results for {facebook_link}]

                - Profile Type: Public (simulated)
                - Last Active: Recently (simulated)
                - Associated Names: John Doe, Jane Smith (simulated)
                - Public Posts: 150 (simulated)
                - Friends Count: 1200 (simulated)
                - Potential Location: New York, USA (simulated)

                Further details from your OSINT modules would appear here.
                """
            else:
                simulated_output = f"""
                [Error] The provided link '{facebook_link}' does not appear to be a valid Facebook URL.
                Please ensure it contains 'facebook.com/'.
                """
            self._append_to_results(simulated_output)
            self.status_bar.config(text=f"Analysis complete for: {facebook_link}")

        except Exception as e:
            error_message = f"An error occurred during analysis: {e}"
            self._append_to_results(f"\n--- ERROR ---\n{error_message}\n")
            self.status_bar.config(text=f"Analysis failed: {e}")
            messagebox.showerror("Analysis Error", error_message)

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
        self.fb_entry.delete(0, tk.END) # Also clear the input field

# Main execution block
if __name__ == "__main__":
    root = tk.Tk()
    app = OSINTApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import requests
import ijson
import io

pip install tkinter
pip install requests
pip install ijson
pip install io


class OSINTApp:
    """
    A simple OSINT (Open Source Intelligence) application with GUI using Tkinter.
    The program will feature API's to pull movie information.  
    """
    def __init__(self, master):
        """
        Initializes the OSINT App.
        Args:
            master: The root Tkinter window (or parent widget).
        """
        self.master = master
        self.master.title("Custom OSINT Tool")
        self.master.geometry('1366x768')
        self.master.configure(bg="#71a3c1") # Background color

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
        tk.Label(self.master, text="Movie OSINT Tool", bg="#71a3c1", font=("Times New Roman", 24, "bold")).grid(
            row=0, column=0, pady=(10, 0), sticky="n" # Centered at the top
        )
        tk.Label(self.master, text="This tool was designed by Tristan Hatfield and programmed by Tristan Hatfield, Petra Kelly, Bryan Bachleda, Adam Lazarowicz", bg="#71a3c1", font=("Times New Roman", 14)).grid(
            row=1, column=0, pady=(0, 10), sticky="n" # Below the title
        )
        tk.Label(self.master, text="The tool will ask for a movie name from the user, then it will provide possible Movie Names, IMDB Information, Where to Stream, and a Movie Trailer. ", bg="#71a3c1", font=("Times New Roman", 14)).grid(
            row=2, column=0, pady=(0, 10), sticky="n" # Below the title
        )

        # --- Input Frame ---
        # This frame will hold the link entries for the APIs and the Analyze button.
        input_frame = ttk.LabelFrame(self.master, text="Analysis", padding="10 10 10 10")
        input_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1) # Allow the entry field to expand

        tk.Label(input_frame, text="Enter the Movie Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.stream_entry = ttk.Entry(input_frame, width=60) # Use ttk.Entry for modern look
        self.stream_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.stream_entry.bind("<Return>", lambda event: self._analyze_data()) # Bind Enter key to analysis

        analyze_button = ttk.Button(input_frame, text="Find Movies", command=self._analyze_data)
        analyze_button.grid(row=1, column=0, columnspan=2, pady=10) # Span across both columns

        # --- Results Display Frame ---
        # This frame will contain the scrolled text area for displaying results.
        results_frame = ttk.LabelFrame(self.master, text="Results", padding="10 10 10 10")
        results_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1) # Make the text area expand vertically
        results_frame.grid_columnconfigure(0, weight=1) # Make the text area expand horizontally

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=80, height=15, font=("Consolas", 10))
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_text.insert(tk.END, "Enter relevant links and click 'Analyze Data' to see results.\n")
        self.results_text.config(state=tk.DISABLED) # Make text area read-only initially

        # Clear Results Button
        clear_button = ttk.Button(results_frame, text="Clear Results", command=self._clear_results)
        clear_button.grid(row=1, column=0, pady=(10, 0)) # Below the text area



    def _analyze_data(self):    
        stream_api = "https://streaming-availability.p.rapidapi.com/shows/search/title"
        stream_url = self.stream_entry.get()
        stream_querystring = {"country":"US","title":stream_url,"output_language":"en"}
        stream_headers = {
                "x-rapidapi-key": "24487241e5msh7d9e4ee01600512p1b9d7ejsn6b28ebd02ccf",
                "x-rapidapi-host": "streaming-availability.p.rapidapi.com"
        }
        response = requests.get(stream_api, headers=stream_headers, params=stream_querystring)
        
        f = io.BytesIO(response.content)
        try:
            items = ijson.items(f, 'item')  # Root-level list of items

            for item in items:
                title = item.get('title', 'Unknown Title')
                self._append_to_results(f"\n🎬 Title: {title}")
                
                imdb_id = item.get('imdbId', 'Unknown ID')
                self._append_to_results(f"\n🎬 IMDB ID: {imdb_id}")
                self._trailer_api(imdb_id)
                self._movie_info(imdb_id)
                self._get_rankings(imdb_id)
                                 
                # Handle streaming options for US
                us_streams = item.get('streamingOptions', {}).get('us', [])
                if us_streams:
                    for stream in us_streams:
                        service = stream.get('service', {}).get('name', 'Unknown Service')
                        price = stream.get('price', {}).get('formatted', 'N/A')
                        link = stream.get('link', 'No link available')
                        self._append_to_results(f"  • {service} | {price} | [Watch]({link})")
                else:
                    self._append_to_results("  ⛔ No US streaming info found.")
        except Exception as e:
            self._append_to_results(f"🚨 Error parsing JSON: {e}")


            
    def _trailer_api(self, imdb_id):
        url = f"https://imdb236.p.rapidapi.com/api/imdb/{imdb_id}"
        headers = {
                "x-rapidapi-key": "24487241e5msh7d9e4ee01600512p1b9d7ejsn6b28ebd02ccf",
                "x-rapidapi-host": "imdb236.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)

        try:
            f = io.BytesIO(response.content) 
            data = next(ijson.items(f, '', use_float=True))  # Parse the root object

            trailer = data.get('trailer', 'No trailer information found.')
            self._append_to_results(f"\n🎬 Trailer: {trailer}")
                
        except Exception as e:
            self._append_to_results(f"🚨 Error parsing JSON: {e}")
    
    
    def _movie_info(self, imdb_id):
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey=a0ff5593"

        response = requests.get(url)

        try:
            f = io.BytesIO(response.content) 
            data = next(ijson.items(f, '', use_float=True))  # Parse the root object

            date = data.get('Released', 'No release date information found.')
            self._append_to_results(f"\nReleased: {date}")
            plot = data.get('Plot', 'No plot information found.')
            self._append_to_results(f"\nPlot: {plot}")
            cast = data.get('Actors', 'No actor information found.')
            self._append_to_results(f"\nCast: {cast}")
                                    
        except Exception as e:
            self._append_to_results(f"🚨 Error parsing JSON: {e}")
            
    def _get_rankings(self, imdb_id):
        url = "https://imdb232.p.rapidapi.com/api/title/get-ratings"

        querystring = {"tt":imdb_id}

        headers = {
                "x-rapidapi-key": "24487241e5msh7d9e4ee01600512p1b9d7ejsn6b28ebd02ccf",
                "x-rapidapi-host": "imdb232.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        
        try:

            f = io.BytesIO(response.content) 
            data = next(ijson.items(f, '', use_float=True))  # Parse the root object

            rating = data.get('rating summary', 'No rating information found.')
            self._append_to_results(f"\nAverage Rating: {rating}")
            votes = data.get('voteCount', 'No votes found.')
            self._append_to_results(f"\n Vote Count: {votes}")
            ranking = data.get('topRanking', 'No ranking information found.')
            self._append_to_results(f"\nRank: {ranking}")
                                    
        except Exception as e:
            self._append_to_results(f"🚨 Error parsing JSON: {e}")
                                
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
        self.stream_entry.delete(0, tk.END) # Also clear the input field

# Main execution block
if __name__ == "__main__":
    root = tk.Tk()
    app = OSINTApp(root)
    root.mainloop()

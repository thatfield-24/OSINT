import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import requests
import threading
import csv
from decimal import Decimal, InvalidOperation
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class OSINTApp:
    """
    A simple OSINT (Open Source Intelligence) application with GUI using Tkinter.
    The program will feature API's to pull movie information and rankings.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Movie OSINT & Analysis Tool")
        self.master.geometry('1366x768')
        self.master.configure(bg="#71a3c1")

        style = ttk.Style()
        style.configure("TFrame", background="#71a3c1")
        style.configure("TLabel", background="#71a3c1", font=("Times New Roman", 12))
        style.configure("Header.TLabel", font=("Times New Roman", 24, "bold"))
        style.configure("SubHeader.TLabel", font=("Times New Roman", 14))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TLabelframe", background="#71a3c1", padding=10)
        style.configure("TLabelframe.Label", background="#71a3c1", font=("Segoe UI", 12, "bold"))

        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_rowconfigure(3, weight=0)
        self.master.grid_columnconfigure(0, weight=1)

        self.movie_results = []
        self.active_buttons = []

        # --- API Keys ---
        self.tmdb_api_key = "51ef0c3ddb3c9a4d0080390f0b674f8a"
        self.rapidapi_key = "24487241e5msh7d9e4ee01600512p1b9d7ejsn6b28ebd02ccf"
        self.omdb_api_key = "a0ff5593"
        
        # TMDb genre IDs needed for the analysis
        self.genre_map = {
            'Action': 28, 'Adventure': 12, 'Animation': 16, 'Comedy': 35,
            'Crime': 80, 'Drama': 18, 'Family': 10751, 'Fantasy': 14,
            'History': 36, 'Horror': 27, 'Music': 10402, 'Mystery': 9648,
            'Romance': 10749, 'Sci-Fi': 878, 'Thriller': 53
        }

        self._create_widgets()

    def _create_widgets(self):
        title_frame = ttk.Frame(self.master, style="TFrame")
        title_frame.grid(row=0, column=0, pady=(10, 5), sticky="n")
        ttk.Label(title_frame, text="Movie OSINT & Analysis Tool", style="Header.TLabel").pack()
        ttk.Label(title_frame, text="Designed by Tristan Hatfield, Programmed by Tristan Hatfield, Petra Kelly, Bryan Bachleda, Adam Lazarowicz", style="SubHeader.TLabel", wraplength=800).pack(pady=(0,10))

        main_input_frame = ttk.Frame(self.master, padding="10", style="TFrame")
        main_input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        main_input_frame.grid_columnconfigure(0, weight=1)
        main_input_frame.grid_columnconfigure(1, weight=1)
        main_input_frame.grid_columnconfigure(2, weight=1)

        single_search_frame = ttk.LabelFrame(main_input_frame, text="Single Movie Search")
        single_search_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        single_search_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(single_search_frame, text="Enter Movie Title:").grid(row=0, column=0, sticky="w")
        self.stream_entry = ttk.Entry(single_search_frame)
        self.stream_entry.grid(row=1, column=0, columnspan=2, padx=(0,5), pady=5, sticky="ew")
        self.stream_entry.bind("<Return>", lambda event: self._start_analysis_thread(self._analyze_single_movie, self.rapidapi_key))
        self.analyze_button = ttk.Button(single_search_frame, text="Find Movie", command=lambda: self._start_analysis_thread(self._analyze_single_movie, self.rapidapi_key))
        self.analyze_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.active_buttons.append(self.analyze_button)

        rankings_frame = ttk.LabelFrame(main_input_frame, text="Top Movies by Year")
        rankings_frame.grid(row=0, column=1, padx=(10, 10), sticky="nsew")
        rankings_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(rankings_frame, text="Enter Year:").grid(row=0, column=0, sticky="w")
        self.year_entry = ttk.Entry(rankings_frame)
        self.year_entry.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        self.year_entry.bind("<Return>", lambda event: self._start_analysis_thread(self._get_top_rankings_by_year, self.tmdb_api_key))
        self.rankings_button = ttk.Button(rankings_frame, text="Get Top 10 Movies", command=lambda: self._start_analysis_thread(self._get_top_rankings_by_year, self.tmdb_api_key))
        self.rankings_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.active_buttons.append(self.rankings_button)
        
        analysis_frame = ttk.LabelFrame(main_input_frame, text="Genre Performance Analysis")
        analysis_frame.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        analysis_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(analysis_frame, text="Enter Year to Analyze:").grid(row=0, column=0, sticky="w")
        self.analysis_year_entry = ttk.Entry(analysis_frame)
        self.analysis_year_entry.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        self.analysis_year_entry.bind("<Return>", lambda event: self._start_analysis_thread(self._analyze_genres_for_year, self.tmdb_api_key))
        self.analysis_button = ttk.Button(analysis_frame, text="Analyze Genres", command=lambda: self._start_analysis_thread(self._analyze_genres_for_year, self.tmdb_api_key))
        self.analysis_button.grid(row=2, column=0, columnspan=2, pady=5)
        self.active_buttons.append(self.analysis_button)

        results_frame = ttk.LabelFrame(self.master, text="Results")
        results_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=80, height=15, font=("Consolas", 10))
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_text.config(state=tk.DISABLED)

        action_frame = ttk.Frame(results_frame, style="TFrame")
        action_frame.grid(row=1, column=0, pady=(10, 0), sticky="e")
        self.export_button = ttk.Button(action_frame, text="Export Results", command=self._export_results)
        self.export_button.pack(side=tk.LEFT, padx=5)
        self.active_buttons.append(self.export_button)
        self.clear_button = ttk.Button(action_frame, text="Clear Results", command=self._clear_results)
        self.clear_button.pack(side=tk.LEFT)
        self.active_buttons.append(self.clear_button)

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=5)
        status_bar.grid(row=3, column=0, sticky="ew")

    def _set_ui_state(self, state):
        if state == 'busy':
            for button in self.active_buttons:
                button.config(state=tk.DISABLED)
            self.status_var.set("Loading... Please wait.")
        else:
            for button in self.active_buttons:
                button.config(state=tk.NORMAL)
            self.status_var.set("Ready")
        self.master.update_idletasks()

    def _start_analysis_thread(self, target_function, *args):
        def thread_wrapper():
            self.master.after(0, self._set_ui_state, 'busy')
            try:
                target_function(*args)
            finally:
                self.master.after(0, self._set_ui_state, 'ready')
        thread = threading.Thread(target=thread_wrapper, daemon=True)
        thread.start()

    def _analyze_genres_for_year(self, api_key):
        self._clear_results(clear_input=False)
        year = self.analysis_year_entry.get()
        if not year.isdigit() or len(year) != 4:
            self._append_to_results("🚨 Please provide a valid 4-digit year for analysis.")
            return

        self._append_to_results(f"Starting genre analysis for {year}...")
        
        all_movie_data = []
        genres_to_analyze = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Fantasy', 'Thriller']

        try:
            for genre_name in genres_to_analyze:
                self.master.after(0, self.status_var.set, f"Fetching data for {genre_name}...")
                
                url = "https://api.themoviedb.org/3/discover/movie"
                params = {
                    "api_key": api_key,
                    "primary_release_year": year,
                    "with_genres": self.genre_map.get(genre_name),
                    "sort_by": "vote_average.desc",
                    "vote_count.gte": 100,
                    "page": "1"
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json().get('results', [])
                
                for movie in data[:5]:
                    all_movie_data.append({
                        "genre": genre_name,
                        "rating": movie.get('vote_average', 0)
                    })

            if not all_movie_data:
                self._append_to_results("⛔ No data found for analysis.")
                return

            self.master.after(0, self.status_var.set, "Analyzing data...")
            df = pd.DataFrame(all_movie_data)
            genre_ratings = df.groupby('genre')['rating'].mean().sort_values(ascending=False)
            
            self._append_to_results("\n--- Average TMDb Rating by Genre for " + year + " ---")
            self._append_to_results(genre_ratings.to_string())
            
            self.master.after(0, self.status_var.set, "Creating plot...")
            plt.style.use('seaborn-v0_8-whitegrid')
            fig, ax = plt.subplots(figsize=(12, 8))
            genre_ratings.sort_values().plot(kind='barh', ax=ax, color='skyblue')
            ax.set_title(f'Average TMDb Movie Rating by Genre for {year}', fontsize=16)
            ax.set_xlabel('Average Rating (TMDb)', fontsize=12)
            ax.set_ylabel('Genre', fontsize=12)
            plt.tight_layout()
            
            image_path = "genre_analysis.png"
            plt.savefig(image_path)
            plt.close(fig)
            
            self.master.after(0, self._display_analysis_plot, image_path)

        except requests.exceptions.RequestException as e:
            self._append_to_results(f"🚨 TMDb Network Error during analysis: {e}")
        except Exception as e:
            self._append_to_results(f"🚨 An error occurred during analysis: {e}")

    def _display_analysis_plot(self, image_path):
        try:
            plot_window = tk.Toplevel(self.master)
            plot_window.title("Genre Analysis Plot")
            
            img = Image.open(image_path)
            tk_img = ImageTk.PhotoImage(img)
            
            lbl = tk.Label(plot_window, image=tk_img)
            lbl.image = tk_img
            lbl.pack(padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Plot Error", f"Could not display the plot image: {e}")

    def _analyze_single_movie(self, api_key):
        self._clear_results(clear_input=False)
        movie_title = self.stream_entry.get()
        if not movie_title:
            self._append_to_results("🚨 Please enter a movie title.")
            return
        self._append_to_results(f"Searching for '{movie_title}'...")
        url = "https://streaming-availability.p.rapidapi.com/shows/search/title"
        querystring = {"country": "us", "title": movie_title, "output_language": "en"}
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "streaming-availability.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            response.raise_for_status()
            json_response = response.json()
            data = json_response.get('result', []) if isinstance(json_response, dict) else json_response
            
            if not data:
                self._append_to_results(f"⛔ No results found for '{movie_title}'.")
                return
            for item in data:
                self._process_streaming_item(item)
        except requests.exceptions.RequestException as e:
            self._append_to_results(f"🚨 Network Error: {e}")
        except Exception as e:
            self._append_to_results(f"🚨 An error occurred during single movie search: {e}")

    def _get_top_rankings_by_year(self, api_key):
        self._clear_results(clear_input=False)
        year = self.year_entry.get()
        if not year.isdigit() or len(year) != 4:
            self._append_to_results("🚨 Please provide a valid 4-digit year.")
            return
        
        self._append_to_results(f"Searching for Top 10 movies of {year} using TMDb...\n")
        
        url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": api_key,
            "primary_release_year": year,
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100,
            "page": "1"
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            movies = data.get('results', [])

            if not movies:
                self._append_to_results(f"⛔ No top-rated movies found for {year}.")
                return

            for movie in movies[:10]:
                tmdb_id = movie.get('id')
                title = movie.get('title')
                rating = movie.get('vote_average')
                overview = movie.get('overview')
                self._process_ranking_item(tmdb_id, title, rating, overview)

        except requests.exceptions.RequestException as e:
            self._append_to_results(f"🚨 TMDb Network Error: {e}")
        except Exception as e:
            self._append_to_results(f"🚨 An error occurred: {e}")

    def _process_ranking_item(self, tmdb_id, title, rating, overview):
        imdb_id = self._get_imdb_id_from_tmdb(tmdb_id)
        if not imdb_id:
            self._append_to_results(f"\n🎬 Title: {title} | Rating: {rating} (Could not find IMDb ID)")
            return

        details = self._get_movie_details_from_omdb(imdb_id)
        if not details:
            self._append_to_results(f"\n🎬 Could not fetch full details for {title}")
            return
        
        details['rating'] = rating # Overwrite OMDb rating with more standard TMDb rating for this list
        movie_data = details
        self.movie_results.append(movie_data)

        self._append_to_results(f"\n🎬 Title: {details['title']} ({details['year']}) | TMDb Rating: {rating}")
        self._append_to_results(f"   IMDb ID: {details['imdb_id']}")
        self._append_to_results(f"   Genre: {details['genre']}")
        self._append_to_results(f"   Plot: {overview}")
        self._append_to_results(f"   Cast: {details['cast']}")
        
    def _get_imdb_id_from_tmdb(self, tmdb_id):
        if not tmdb_id: return None
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {"api_key": self.tmdb_api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('imdb_id')
        except Exception:
            return None

    def _process_streaming_item(self, item):
        title = item.get('title', 'N/A')
        imdb_id = item.get('imdbId', 'N/A')
        details = self._get_movie_details_from_omdb(imdb_id)
        
        if not details:
            self._append_to_results(f"\n🎬 Could not fetch details for {title}")
            return

        movie_data = details
        self.movie_results.append(movie_data)

        self._append_to_results(f"\n🎬 Title: {title} ({details['year']}) | IMDb Rating: {details['rating']}")
        self._append_to_results(f"   IMDb ID: {imdb_id}")
        self._append_to_results(f"   Genre: {details['genre']}")
        self._append_to_results(f"   Plot: {details['plot']}")
        self._append_to_results(f"   Cast: {details['cast']}")
        
        us_streams = item.get('streamingOptions', {}).get('us', [])
        if us_streams:
            self._append_to_results("   Streaming on:")
            for stream in us_streams:
                service = stream.get('service', {}).get('name', 'N/A')
                link = stream.get('link', '#')
                self._append_to_results(f"     • {service}: {link}")
        else:
            self._append_to_results("   ⛔ No US streaming info found.")

    def _get_movie_details_from_omdb(self, imdb_id):
        if not imdb_id: return None
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={self.omdb_api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "False": return None
            
            genre_full_string = data.get('Genre', 'N/A')
            main_genre = genre_full_string.split(',')[0].strip()
            
            try:
                rating = Decimal(data.get('imdbRating', '0'))
            except (InvalidOperation, TypeError):
                rating = None

            return {
                "imdb_id": imdb_id,
                "title": data.get('Title', 'N/A'),
                "genre": main_genre,
                "plot": data.get('Plot', 'N/A'),
                "cast": data.get('Actors', 'N/A'),
                "year": data.get('Year', 'N/A'),
                "rating": rating
            }
        except Exception:
            return None

    def _export_results(self):
        if not self.movie_results:
            messagebox.showwarning("No Data", "There is no data to export.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], title="Save Results As")
        if not filepath: return
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                headers = ['imdb_id', 'title', 'year', 'rating', 'genre', 'plot', 'cast']
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(self.movie_results)
            messagebox.showinfo("Success", f"Results successfully exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {e}")

    def _append_to_results(self, text):
        self.master.after(0, self._do_append, text)

    def _do_append(self, text):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def _clear_results(self, clear_input=True):
        self.master.after(0, self._do_clear, clear_input)
    
    def _do_clear(self, clear_input):
        self.movie_results.clear()
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Results cleared. Ready for new analysis.\n")
        self.results_text.config(state=tk.DISABLED)
        self.status_var.set("Ready")
        if clear_input:
            self.stream_entry.delete(0, tk.END)
            self.year_entry.delete(0, tk.END)
            self.analysis_year_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = OSINTApp(root)
    root.mainloop()
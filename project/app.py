import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from analyzers import (
    get_website_data,
    analyze_common_words,
    analyze_product_popularity,
    analyze_price_range,
    analyze_best_selling_products,
    analyze_meta_tags,
    analyze_headings,
    analyze_links,
    analyze_images,
    analyze_page_load_time,
    analyze_word_count,
    analyze_keyword_density
)

class WebsiteAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("E-commerce Website Analyzer")
        self.master.geometry("1200x800")
        self.master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 12))
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))
        self.style.configure("TCombobox", font=("Arial", 12))

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(url_frame, text="Enter website URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # Analysis options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(options_frame, text="Select analysis type:").pack(side=tk.LEFT)
        self.analysis_type = tk.StringVar()
        analysis_options = [
            "Product popularity",
            "Price range",
            "Best-selling products",
            "Most common words",
            "Meta tags",
            "Headings",
            "Links",
            "Images",
            "Page load time",
            "Word count",
            "Keyword density"
        ]
        self.analysis_combobox = ttk.Combobox(options_frame, textvariable=self.analysis_type, values=analysis_options, state="readonly")
        self.analysis_combobox.pack(side=tk.LEFT, padx=5)
        self.analysis_combobox.set(analysis_options[0])

        self.analyze_button = ttk.Button(options_frame, text="Analyze", command=self.analyze_website)
        self.analyze_button.pack(side=tk.LEFT, padx=(20, 0))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))

        # Results area
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Graph area
        self.graph_frame = ttk.Frame(results_frame)
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Text results area
        self.text_result = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=40, font=("Arial", 10))
        self.text_result.pack(side=tk.RIGHT, fill=tk.Y)

    def analyze_website(self):
        url = self.url_entry.get()
        analysis_type = self.analysis_type.get()

        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        self.progress_var.set(0)
        self.analyze_button.config(state="disabled")
        self.master.update()

        html = get_website_data(url)
        if html:
            self.progress_var.set(50)
            self.master.update()

            if analysis_type == "Product popularity":
                data = analyze_product_popularity(html)
            elif analysis_type == "Price range":
                data = analyze_price_range(html)
            elif analysis_type == "Best-selling products":
                data = analyze_best_selling_products(html)
            elif analysis_type == "Most common words":
                data = analyze_common_words(html)
            elif analysis_type == "Meta tags":
                data = analyze_meta_tags(html)
            elif analysis_type == "Headings":
                data = analyze_headings(html)
            elif analysis_type == "Links":
                data = analyze_links(html, url)
            elif analysis_type == "Images":
                data = analyze_images(html)
            elif analysis_type == "Page load time":
                data = analyze_page_load_time(url)
            elif analysis_type == "Word count":
                data = analyze_word_count(html)
            elif analysis_type == "Keyword density":
                data = analyze_keyword_density(html)
            else:
                messagebox.showerror("Error", "Invalid analysis type")
                return

            self.progress_var.set(75)
            self.master.update()

            if data:
                self.create_graph(data, analysis_type)
                self.update_text_result(data, analysis_type)
            else:
                self.show_no_data_message(analysis_type)
        else:
            messagebox.showerror("Error", "Failed to retrieve website data")

        self.progress_var.set(100)
        self.analyze_button.config(state="normal")

    def create_graph(self, data, title):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        
        if all(isinstance(item[1], (int, float)) for item in data):
            x, y = zip(*data)
            ax.bar(x, y)
            ax.set_xlabel('Items')
            ax.set_ylabel('Value')
            plt.xticks(rotation=45, ha='right')
        elif title == "Meta tags":
            ax.axis('off')
            ax.text(0.5, 0.5, "Meta tags information available in text results", 
                    ha='center', va='center', fontsize=12)
        else:
            # Filter out non-numeric values and create a pie chart
            numeric_data = [(item[0], item[1]) for item in data if isinstance(item[1], (int, float))]
            if numeric_data:
                labels, sizes = zip(*numeric_data)
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
            else:
                ax.axis('off')
                ax.text(0.5, 0.5, "No numeric data available for graphing", 
                        ha='center', va='center', fontsize=12)

        ax.set_title(title)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH)
        canvas.draw()

    def update_text_result(self, data, analysis_type):
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, f"{analysis_type} Results:\n\n")
        
        if analysis_type == "Meta tags":
            for name, content in data:
                self.text_result.insert(tk.END, f"{name}: {content}\n\n")
        else:
            for item, value in data:
                if isinstance(value, float):
                    self.text_result.insert(tk.END, f"{item}: {value:.2f}\n")
                else:
                    self.text_result.insert(tk.END, f"{item}: {value}\n")

    def show_no_data_message(self, analysis_type):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        message = f"No data found for {analysis_type}"
        label = ttk.Label(self.graph_frame, text=message, font=("Arial", 14))
        label.pack(expand=True)

        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, message)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebsiteAnalyzerApp(root)
    root.mainloop()
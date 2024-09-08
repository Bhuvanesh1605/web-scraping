import tkinter as tk
from app import WebsiteAnalyzerApp

def main():
    root = tk.Tk()
    root.title("Website Analyzer")
    root.geometry("1200x800")
    app = WebsiteAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

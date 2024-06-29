import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import openpyxl
from collections import defaultdict

class SKTMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SKTM Classification")
        
        self.load_button = tk.Button(root, text="Load Excel File", command=self.load_file)
        self.load_button.pack(pady=10)
        
        self.frame = ttk.Frame(root)
        self.frame.pack(pady=10)
        
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(pady=10)
        
        self.entries = {}
        self.create_input_form()
        
        self.classify_button = tk.Button(root, text="Classify", command=self.classify)
        self.classify_button.pack(pady=10)
        
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.process_data(file_path)

    def create_input_form(self):
        labels = ["Pekerjaan", "Usia", "Status", "Penghasilan", "Kendaraan", "Kepemilikan", "Atap Bangunan"]
        self.labels = labels
        for i, label in enumerate(labels):
            lbl = tk.Label(self.input_frame, text=label)
            lbl.grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(self.input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = entry

    def process_data(self, file_path):
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Read the data into a list of dictionaries
        self.data = []
        columns = ["No", "Nama", "Pekerjaan", "Usia", "Status", "Penghasilan", "Kendaraan", "Kepemilikan", "Atap Bangunan", "Keterangan"]
        for row in sheet.iter_rows(min_row=2, values_only=True):
            self.data.append(dict(zip(columns, row)))
        
        # Count occurrences of each class in 'Keterangan'
        self.total_count = len(self.data)
        self.layak_count = sum(1 for row in self.data if row["Keterangan"] == "layak")
        self.tidak_layak_count = self.total_count - self.layak_count
        
        # Display counts in console
        print(f"Jumlah yang layak: {self.layak_count}")
        print(f"Jumlah yang tidak layak: {self.tidak_layak_count}")
        
        # Calculate probabilities
        self.prob_layak = self.layak_count / self.total_count
        self.prob_tidak_layak = self.tidak_layak_count / self.total_count

        # Display probabilities in console
        print(f"Probabilitas Kelas Layak (P(layak)): {self.prob_layak}")
        print(f"Probabilitas Kelas Tidak Layak (P(tidak layak)): {self.prob_tidak_layak}")

    def classify(self):
        input_data = {label: entry.get().strip() for label, entry in self.entries.items()}
        
        # Calculate feature probabilities
        feature_probabilities = defaultdict(lambda: {"layak": 0, "tidak layak": 0})
        
        for row in self.data:
            for label in self.labels:
                if row[label] == input_data[label]:
                    if row["Keterangan"] == "layak":
                        feature_probabilities[label]["layak"] += 1
                    else:
                        feature_probabilities[label]["tidak layak"] += 1
        
        for label in self.labels:
            if self.layak_count > 0:
                feature_probabilities[label]["layak"] /= self.layak_count
            if self.tidak_layak_count > 0:
                feature_probabilities[label]["tidak layak"] /= self.tidak_layak_count
        
        # Calculate the final probabilities for layak and tidak layak
        prob_layak_final = self.prob_layak
        prob_tidak_layak_final = self.prob_tidak_layak

        print("\nPerhitungan probabilitas fitur:")
        for label in self.labels:
            prob_layak_final *= feature_probabilities[label]['layak']
            prob_tidak_layak_final *= feature_probabilities[label]['tidak layak']
            print(f"{label} = {input_data[label]} | P({label} | layak): {feature_probabilities[label]['layak']:.4f}, P({label} | tidak layak): {feature_probabilities[label]['tidak layak']:.4f}")
        
        # Display final probabilities in console
        print(f"\nHasil kali probabilitas fitur dengan kelas layak: {prob_layak_final / self.prob_layak}")
        print(f"Hasil kali probabilitas fitur dengan kelas tidak layak: {prob_tidak_layak_final / self.prob_tidak_layak}")

        print(f"\nProbabilitas akhir Layak: {prob_layak_final}")
        print(f"Probabilitas akhir Tidak Layak: {prob_tidak_layak_final}")
        
        # Calculate normalized probabilities
        prob_sum = prob_layak_final + prob_tidak_layak_final
        normalized_prob_layak = prob_layak_final / prob_sum
        normalized_prob_tidak_layak = prob_tidak_layak_final / prob_sum

        # Display normalized probabilities in console
        print(f"\nProbabilitas normalisasi Layak: {normalized_prob_layak}")
        print(f"Probabilitas normalisasi Tidak Layak: {normalized_prob_tidak_layak}")
        
        # Determine classification
        classification = "layak" if normalized_prob_layak > normalized_prob_tidak_layak else "tidak layak"
        
        # Display classification result in a message box
        messagebox.showinfo("Hasil Klasifikasi", f"Hasil Klasifikasi: {classification}\n\nProbabilitas Layak: {normalized_prob_layak:.4f}\nProbabilitas Tidak Layak: {normalized_prob_tidak_layak:.4f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SKTMApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("🔬 Analisador de Fibras em Escala Nanométrica")
        master.geometry("850x750")
        master.configure(bg="#2C3E50")

        # Variáveis
        self.image_path = tk.StringVar()
        self.cutoff = tk.IntVar(value=872)
        self.ppm = tk.DoubleVar(value=47)

        title_style = {"font": ("Helvetica", 16, "bold"), "bg": "#2C3E50", "fg": "#ECF0F1"}
        label_style = {"font": ("Helvetica", 12), "bg": "#2C3E50", "fg": "#ECF0F1"}
        button_style = {"font": ("Helvetica", 12, "bold"), "bg": "#3498DB", "fg": "#FFFFFF", "activebackground": "#2980B9"}

        # Título
        tk.Label(master, text="🔬 Analisador de Fibras em Escala Nanométrica", **title_style).pack(pady=10)

        # Seleção da imagem
        tk.Label(master, text="Selecione a Imagem:", **label_style).pack(pady=5)
        tk.Button(master, text="Carregar Imagem", command=self.load_image, **button_style).pack(pady=5)

        self.image_label = tk.Label(master, bg="#2C3E50")
        self.image_label.pack(pady=10)

        # Configurações
        settings_frame = tk.Frame(master, bg="#34495E")
        settings_frame.pack(pady=10, fill=tk.X, padx=20)

        tk.Label(settings_frame, text="Cutoff (pixels):", **label_style).pack(pady=5)
        tk.Scale(settings_frame, from_=1, to=2000, orient='horizontal', variable=self.cutoff, bg="#34495E", fg="#ECF0F1").pack(pady=5)

        tk.Label(settings_frame, text="Pixels por Micrômetro:", **label_style).pack(pady=5)
        tk.Entry(settings_frame, textvariable=self.ppm, font=("Helvetica", 12)).pack(pady=5)

        tk.Button(master, text="Analisar Imagem", command=self.analyze_image, **button_style).pack(pady=10)

        self.output_text = tk.Text(master, height=10, font=("Helvetica", 11), bg="#34495E", fg="#ECF0F1")
        self.output_text.pack(pady=10, fill=tk.BOTH, padx=20)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.image_path.set(file_path)
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=img)
            self.image_label.image = img

    def analyze_image(self):
        if not self.image_path.get():
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return

        image = cv2.imread(self.image_path.get())
        cutoff = self.cutoff.get()
        PixelsPerMicrometer = self.ppm.get()

        cropped_image = image[:cutoff, :]
        display_image = cropped_image.copy()

        height, width, _ = cropped_image.shape
        half_width = width // 2
        half_height = height // 2

        quadrants = [
            cropped_image[0:half_height, 0:half_width],
            cropped_image[0:half_height, half_width:],
            cropped_image[half_height:, 0:half_width],
            cropped_image[half_height:, half_width:]
        ]

        diameters = []
        all_diameters_nm = []

        for idx, quadrant in enumerate(quadrants):
            gray = cv2.cvtColor(quadrant, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            quadrant_diameters = []

            offset_x = (idx % 2) * half_width
            offset_y = (idx // 2) * half_height

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                diameter = min(w, h)
                quadrant_diameters.append(diameter)
                all_diameters_nm.append(round(1000 * diameter / PixelsPerMicrometer, 4))
                cv2.rectangle(display_image, (x+offset_x, y+offset_y), (x+w+offset_x, y+h+offset_y), (0, 255, 0), 1)

            mean_diameter_px = np.mean(quadrant_diameters[:50])
            mean_diameter_um = mean_diameter_px / PixelsPerMicrometer
            diameters.append(mean_diameter_um)

        overall_mean_nm = 1000 * np.mean(diameters)

        result = f"Diâmetro médio: {overall_mean_nm:.2f} nm\n\nDiâmetros medidos (nm): {all_diameters_nm}"

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, result)

        display_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
        display_image = Image.fromarray(display_image)
        display_image.thumbnail((400, 400))
        display_image = ImageTk.PhotoImage(display_image)

        self.image_label.configure(image=display_image)
        self.image_label.image = display_image


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageAnalyzerApp(root)
    root.mainloop()

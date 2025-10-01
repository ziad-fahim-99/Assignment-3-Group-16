import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
from models import TextToImageModelWrapper, ImageModelWrapper
from utils import simple_logger, timeit
from PIL import Image, ImageTk

# Multiple-inheritance example: App inherits from tk.Tk and a mixin
class UIMixin:
    def center_window(self, win, w=900, h=600):
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

class App(tk.Tk, UIMixin):
    def __init__(self):
        super().__init__()
        self.title('HIT137 - Assignment 3 (Group)')
        self.center_window(self)

        # encapsulated attributes
        self._text_model = TextToImageModelWrapper()
        self._image_model = ImageModelWrapper()

        self._create_widgets()

    def _create_widgets(self):
        # Top controls
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=8, pady=6)

        ttk.Label(frame, text='Select input type:').pack(side='left', padx=(0,6))
        self.input_var = tk.StringVar(value='text')
        input_select = ttk.Combobox(
            frame, textvariable=self.input_var,
            values=['text-to-image','image-classification'],
            state='readonly', width=20
        )
        input_select.pack(side='left')
        input_select.bind('<<ComboboxSelected>>', lambda e: self._update_input_area())

        run_btn = ttk.Button(frame, text='Run Model', command=self.run_selected_model)
        run_btn.pack(side='right')

        info_btn = ttk.Button(frame, text='Model Info', command=self.show_model_info)
        info_btn.pack(side='right', padx=6)

        # Input area
        self.input_area = ttk.Frame(self)
        self.input_area.pack(fill='both', expand=True, padx=8, pady=6)
        self._update_input_area()

        # Output area
        out_label = ttk.Label(self, text='Output:')
        out_label.pack(anchor='w', padx=8)
        self.output_frame = ttk.Frame(self)
        self.output_frame.pack(fill='both', padx=8, pady=(0,8), expand=True)

        # Explanation area
        expl_label = ttk.Label(self, text='OOP Concepts and Model Explanation:')
        expl_label.pack(anchor='w', padx=8)
        self.expl_text = scrolledtext.ScrolledText(self, height=8)
        self.expl_text.pack(fill='both', padx=8, pady=(0,8), expand=False)
        self._fill_explanations()

    def _update_input_area(self):
        for w in self.input_area.winfo_children():
            w.destroy()
        itype = self.input_var.get()
        if itype == 'text-to-image':
            ttk.Label(self.input_area, text='Enter text prompt:').pack(anchor='w')
            self.text_entry = scrolledtext.ScrolledText(self.input_area, height=6)
            self.text_entry.pack(fill='both', expand=True)
        else:
            ttk.Label(self.input_area, text='Select image file:').pack(anchor='w')
            file_frame = ttk.Frame(self.input_area)
            file_frame.pack(fill='x')
            self.image_path_var = tk.StringVar()
            ttk.Entry(file_frame, textvariable=self.image_path_var, width=60).pack(side='left', padx=(0,6))
            ttk.Button(file_frame, text='Browse', command=self.browse_image).pack(side='left')

            # area to show thumbnail
            self.thumb_label = ttk.Label(self.input_area)
            self.thumb_label.pack(pady=6)

    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[('Image files','*.png;*.jpg;*.jpeg;*.bmp;*.gif')])
        if path:
            self.image_path_var.set(path)
            try:
                img = Image.open(path)
                img.thumbnail((240,240))
                self._thumb = ImageTk.PhotoImage(img)
                self.thumb_label.configure(image=self._thumb)
            except Exception as e:
                messagebox.showerror('Image error', str(e))

    def _clear_output(self):
        for w in self.output_frame.winfo_children():
            w.destroy()

    @simple_logger
    @timeit
    def run_selected_model(self):
        self._clear_output()
        itype = self.input_var.get()
        try:
            if itype == 'text-to-image':
                prompt = self.text_entry.get('1.0','end').strip()
                if not prompt:
                    messagebox.showwarning('Input required', 'Please enter a text prompt.')
                    return
                result_img = self._text_model.run(prompt)  # PIL image
                # show in GUI
                img_resized = result_img.copy()
                img_resized.thumbnail((400,400))
                self._result_thumb = ImageTk.PhotoImage(img_resized)
                lbl = ttk.Label(self.output_frame, image=self._result_thumb)
                lbl.pack()
            else:
                imgpath = self.image_path_var.get().strip()
                if not imgpath:
                    messagebox.showwarning('Input required', 'Please select an image file.')
                    return
                result = self._image_model.run(imgpath)
                txt = scrolledtext.ScrolledText(self.output_frame, height=6)
                txt.insert('end', result)
                txt.pack(fill='both', expand=True)
        except Exception as e:
            txt = scrolledtext.ScrolledText(self.output_frame, height=6)
            txt.insert('end', f"Error running model: {e}\n")
            txt.insert('end', "Make sure you installed diffusers/torch/transformers and have internet for model download.\n")
            txt.pack(fill='both', expand=True)

    def show_model_info(self):
        info = (
            f"Text-to-Image model: {self._text_model._model_name} (task: text-to-image)\n"
            f"Image Classification model: {self._image_model._model_name} (task: image-classification)\n\n"
            "Notes:\n"
            "- Models are loaded lazily the first time you run them.\n"
            "- Stable Diffusion may take a while to generate images.\n"
            "- Use GPU if available for faster performance.\n"
        )
        messagebox.showinfo('Model Info', info)

    def _fill_explanations(self):
        text = (
            "OOP Concepts used in the project:\n\n"
            "1) Encapsulation:\n"
            "   - Model wrappers (models.py) keep model name and pipeline as private attributes (_).\n\n"
            "2) Polymorphism and Method overriding:\n"
            "   - BaseModelWrapper defines run(); subclasses override run() for each model type.\n\n"
            "3) Multiple Inheritance:\n"
            "   - App inherits from tk.Tk and UIMixin.\n\n"
            "4) Multiple decorators:\n"
            "   - run_selected_model uses @simple_logger and @timeit.\n\n"
            "5) Project Structure:\n"
            "   - Code split into models.py, gui.py, utils.py, main.py.\n\n"
            "Instructions to run:\n"
            " - Create a virtual environment.\n"
            " - Install: pip install transformers torch pillow diffusers accelerate safetensors\n"
            " - Run: python main.py\n"
        )
        self.expl_text.insert('end', text)
        self.expl_text.configure(state='disabled')
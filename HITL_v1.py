import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

'''
def load_image(self):
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if file_path:
        self.img = Image.open(file_path)
        self.update_image_display()
'''

def start_webcam():
    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (200, 200))
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            webcam_display.create_image(0, 0, anchor=tk.NW, image=img_tk)
            webcam_display.image = img_tk  # Keep a reference to avoid garbage collection
        webcam_display.after(10, update_frame)

    cap = cv2.VideoCapture(0)
    update_frame()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("HITL Eye-Tracking Interaction")
        
        # Create a frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # Create buttons
        load_image_button = ttk.Button(button_frame, text="Load Image", command=self.load_image)
        load_image_button.pack(side=tk.LEFT, padx=5, pady=5)

        start_webcam_button = ttk.Button(button_frame, text="Start Webcam", command=start_webcam)
        start_webcam_button.pack(side=tk.LEFT, padx=5, pady=5)

        start_webcam_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Main display area
        display_frame = ttk.Frame(self)
        display_frame.pack(expand=True, fill=tk.BOTH)

        # Image display
        self.image_display = tk.Canvas(display_frame, width=1000, height=800, bg='lightgrey')
        self.image_display.create_text(500, 400, text="Image Display", fill="black")
        self.image_display.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(1, 1), pady=(1,1))
        #self.image_display = tk.Label(display_frame, width=1000, height=800, bg='lightgrey', text='Image Display') 
        #self.image_display.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(1, 1), pady=(1,1))

        self.image_display.bind("<Configure>", self.on_canvas_resize)

        # Webcam and secondary areas
        right_frame = ttk.Frame(display_frame, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Webcam display
        global webcam_display
        webcam_display = tk.Canvas(right_frame, width=200, height=200, bg='lightgrey')
        webcam_display.create_text(100, 100, text="WebCam", fill="black")
        webcam_display.pack(padx=(1,1), pady=(1, 1))

        # Placeholder for the Text input
        default_font = ("Arial", 16)
        adjustable_area = tk.Text(right_frame, width=10, height=50, bg="white", 
                                  fg='black', insertbackground="black",
                                  font=default_font)
        adjustable_area.pack(expand=True, fill=tk.BOTH, padx=(1, 1), pady=(1, 1))
        adjustable_area.focus_set()

        self.photo = None
        self.img = None

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.img = Image.open(file_path)
            self.update_image_display()    

    def update_image_display(self):
        if self.img:
            max_width = self.image_display.winfo_width()
            max_height = self.image_display.winfo_height()
            
            width_scale = max_width / self.img.width
            height_scale = max_height / self.img.height
            scale = min(width_scale, height_scale)

            new_width = int(self.img.width * scale)
            new_height = int(self.img.height * scale)

            resized_img = self.img.resize((new_width, new_height), Image.LANCZOS)

            #self.img.thumbnail((max_width, max_height))
            self.photo = ImageTk.PhotoImage(resized_img)

            self.image_display.delete("all")

            x = (max_width - new_width) // 2
            y = (max_height - new_height) // 2 
            #x = (width - self.photo.width()) // 2
            #y = (height - self.photo.height()) // 2

            self.image_display.create_image(x, y, anchor=tk.NW, image=self.photo)

    def on_canvas_resize(self, event):
        self.update_image_display()

if __name__ == "__main__":
    app = Application()
    app.mainloop()

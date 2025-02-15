import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# 初始化模型
model = WhisperModel(
    "small",#可设置'tiny', 'base', 'small'等
    device="cpu",
    compute_type="float32",
    download_root=r'D:\develop\project\eye_move\model'
)

# 创建界面
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HITL Eye-Tracking Interaction")

        # 创建一个按钮框架
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # 创建按钮
        load_image_button = ttk.Button(button_frame, text="Load Image", command=self.load_image)
        load_image_button.pack(side=tk.LEFT, padx=5, pady=5)

        start_webcam_button = ttk.Button(button_frame, text="Start Webcam", command=self.start_webcam)
        start_webcam_button.pack(side=tk.LEFT, padx=5, pady=5)

        start_audio_button = ttk.Button(button_frame, text="Start Audio", command=self.start_audio)
        start_audio_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 主显示区域
        display_frame = ttk.Frame(self)
        display_frame.pack(expand=True, fill=tk.BOTH)

        # 图像显示区域
        self.image_display = tk.Canvas(display_frame, width=1000, height=800, bg='lightgrey')
        self.image_display.create_text(500, 400, text="Image Display", fill="black")
        self.image_display.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(1, 1), pady=(1, 1))

        # 视频和其他区域
        right_frame = ttk.Frame(display_frame, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # WebCam显示区域
        self.webcam_display = tk.Canvas(right_frame, width=200, height=200, bg='lightgrey')
        self.webcam_display.create_text(100, 100, text="WebCam", fill="black")
        self.webcam_display.pack(padx=(1, 1), pady=(1, 1))

        # 文字输入框
        default_font = ("KaiTi", 12)
        self.text_area = tk.Text(right_frame, width=10, height=50, bg="white", 
                                  fg='black', insertbackground="black",
                                  font=default_font)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=(1, 1), pady=(1, 1))
        self.text_area.focus_set()

        self.photo = None
        self.img = None
        self.audio_buffer = np.array([], dtype=np.float32)
        self.min_duration = 10  # 最小处理时长（秒）

    def start_webcam(self):
        def update_frame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (200, 200))
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                self.webcam_display.create_image(0, 0, anchor=tk.NW, image=img_tk)
                self.webcam_display.image = img_tk  # 保持对图像的引用，避免被垃圾回收
            self.webcam_display.after(10, update_frame)

        cap = cv2.VideoCapture(0)
        update_frame()

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

            self.photo = ImageTk.PhotoImage(resized_img)

            self.image_display.delete("all")

            x = (max_width - new_width) // 2
            y = (max_height - new_height) // 2 

            self.image_display.create_image(x, y, anchor=tk.NW, image=self.photo)

    def on_canvas_resize(self, event):
        self.update_image_display()

    def start_audio(self):
        def update_text_box(text):
            self.text_area.insert(tk.END, text + "\n")
            self.text_area.see(tk.END)

        def process_audio(audio_data):
            try:
                # 移除sample_rate参数
                segments, _ = model.transcribe(
                    audio_data,
                    initial_prompt='我没听清楚,请您再说一遍~',
                    task='transcribe',
                    vad_filter=True  # 语音活动检测
                )
                full_text = " ".join([seg.text for seg in segments])
                if full_text:
                    self.after(0, update_text_box, f">> {full_text}")
            except Exception as e:
                print(f"处理出错: {str(e)}")

        def callback(indata, frames, time, status):
            if status:
                print(f"音频流状态: {status}")
            mono_audio = indata.mean(axis=1).astype(np.float32)
            self.audio_buffer = np.concatenate((self.audio_buffer, mono_audio))
            if len(self.audio_buffer) >= 16000 * self.min_duration:
                process_audio(self.audio_buffer.copy())
                self.audio_buffer = np.array([], dtype=np.float32)

        # 启动音频流
        stream = sd.InputStream(
            callback=callback,
            samplerate=16000,
            channels=1,
            dtype='float32'
        )
        stream.start()


if __name__ == "__main__":
    app = Application()
    app.mainloop()

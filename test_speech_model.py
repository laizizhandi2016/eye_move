import sounddevice as sd
import tkinter as tk
import numpy as np
from faster_whisper import WhisperModel

# 初始化模型（关键修改点）
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="float32",
    download_root=r'D:\develop\project\eye_move\model'
)

# 创建界面
root = tk.Tk()
text_box = tk.Text(root, height=10, width=50)
text_box.pack()

audio_buffer = np.array([], dtype=np.float32)
min_duration = 10  # 最小处理时长（秒）

def update_text_box(text):
    text_box.insert(tk.END, text + "\n")
    text_box.see(tk.END)

def process_audio(audio_data):
    try:
        # 移除了 sample_rate 参数（关键修改点）
        segments, _ = model.transcribe(
            audio_data,
            #language='zh',
            initial_prompt='我是你的语音专家，有什么话可以给我说',
            task='transcribe',
            vad_filter=True  # 语音活动检测
        )
        full_text = " ".join([seg.text for seg in segments])
        if full_text:
            root.after(0, update_text_box, f">> {full_text}")
    except Exception as e:
        print(f"处理出错: {str(e)}")

def callback(indata, frames, time, status):
    global audio_buffer
    if status:
        print(f"音频流状态: {status}")
    mono_audio = indata.mean(axis=1).astype(np.float32)
    audio_buffer = np.concatenate((audio_buffer, mono_audio))
    if len(audio_buffer) >= 16000 * min_duration:
        process_audio(audio_buffer.copy())
        audio_buffer = np.array([], dtype=np.float32)

# 确保音频输入参数正确（关键修改点）
stream = sd.InputStream(
    callback=callback,
    samplerate=16000,  # sounddevice库的参数名是 samplerate
    channels=1,
    dtype='float32'
)
stream.start()

root.mainloop()
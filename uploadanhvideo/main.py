import tkinter as tk
import cv2
import numpy as np
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading

class GUI:
    original_img = None
    processed_img = None
    def __init__(self):
        # Cấu hình
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("Doan opencv")  # Tiêu đề của cửa sổ

        # Header
        self.label = tk.Label(self.root, text="Theo Dõi chuyển động Và Bộ Lọc Ảnh", font=('Arial', 18))
        self.label.pack(padx=20, pady=20)

        button_frame = tk.Frame(self.root)
        button_frame.pack()
        # button
        self.button = tk.Button(button_frame, text="Tải ảnh hoặc video", font=("Arial", 12), command=self.upload_form)
        self.button.pack(side=tk.LEFT,padx=10, pady=10)

        self.selected_effect = tk.StringVar(self.root)
        self.selected_effect.set("Chọn hiệu ứng")  # default value

        self.effect_options = ['Grayscale', 'Sepia', 'Blur']
        self.effect_menu = tk.OptionMenu(button_frame, self.selected_effect, *         self.effect_options, command=self.apply_effect)
        self.effect_menu.pack(side=tk.LEFT, padx=10, pady=10)

        self.button = tk.Button(button_frame, text="Lưu ảnh", font=("Arial", 12), command=self.save_image)
        self.button.pack(side=tk.LEFT,padx=10, pady=10)

        self.button = tk.Button(button_frame, text="Xoá tất cả", font=("Arial", 12), command=self.clear_form)
        self.button.pack(side=tk.LEFT,padx=10, pady=10)
        self.image_label = tk.Label(self.root)
        self.image_label.pack(padx=10, pady=10)
         
        # Mainloop để hiển thị cửa sổ
        self.root.mainloop()
    #ham
    def upload_form(self):
        dinhdang = [('Ảnh JPEG', '*.jpg'), ('Ảnh PNG', '*.png'), ('Video MP4', '*.mp4')]
        filename = filedialog.askopenfilename(filetypes=dinhdang)
        if filename:
            if filename.lower().endswith('.png') or filename.lower().endswith('.jpg'):
                self.original_img = cv2.imread(filename)
                if self.original_img is not None:
                    self.processed_img = self.original_img.copy()  # Sao chép ảnh gốc
                    self.display_image(self.original_img)  # Hiển thị ảnh gốc
                else:
                    messagebox.showwarning("Lỗi", "Không thể đọc ảnh")
            elif filename.lower().endswith('.mp4'):
                    xulyvideo(self,filename)
    def clear_form(self):
        global original_img, processed_img
        original_img = None
        processed_img = None
        self.image_label.configure(image='')
        self.image_label.image = None
        messagebox.showinfo("Thông báo", "Xóa ảnh thành công")
    def save_image(self):
        if self.processed_img is not None:
            filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", ".png"),("JPEG files", ".jpg"),("All files", ".")])
        if filepath:
            if filepath.lower().endswith('.jpg'):
                cv2.imwrite(filepath, cv2.cvtColor(self.processed_img, cv2.COLOR_BGR2RGB))
            else:
                cv2.imwrite(filepath, self.processed_img)
            messagebox.showinfo("Thông báo", "Ảnh đã được tải xuống")
        else:
            messagebox.showwarning("Lỗi", "Ảnh chưa được tải xuống")
    def apply_effect(self,effect):
        if self.original_img is None:
            messagebox.showwarning("Lỗi", "Không thể tạo ảnh")
            return
        if effect == 'Grayscale':
            self.processed_img = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        elif effect == 'Sepia':
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
            self.processed_img = cv2.transform(self.original_img, sepia_filter)
            self.processed_img = np.clip(self.processed_img, 0, 255).astype(np.uint8)
        elif effect == 'Blur':
            self.processed_img = cv2.GaussianBlur(self.original_img, (21, 21), 0)
        else:
            messagebox.showinfo("Thông báo", "Tạo ảnh thành công")
        self.display_image(self.processed_img)
    def display_image(self,img):
        if len(img.shape) == 2:  # Grayscale image
            img_display = Image.fromarray(img)
        else:  # Color image
            img_display = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        img_tk = ImageTk.PhotoImage(img_display)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk
class xulyvideo:
    def __init__(self, parent,filename):
        self.video_label = None
        self.parent = parent
        self.root = tk.Toplevel(self.parent.root)
        self.root.title("Video Player")
        self.root.geometry("800x700")

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        frame_width = 200
        frame_height = 200
        self.cap = cv2.VideoCapture(filename)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        self.out = cv2.VideoWriter("output.avi", fourcc, 5.0, (1280,720))

        self.ret, self.frame1 = self.cap.read()
        self.ret, self.frame2 = self.cap.read()
        self.play_thread = threading.Thread(target=self.play_video)
        self.play_thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
    def play_video(self):
        while self.cap.isOpened():
            if not self.root.winfo_exists():
                break
            if self.video_label is None or not self.video_label.winfo_exists():
                if self.root.winfo_exists():
                    self.video_label = tk.Label(self.root)
                    self.video_label.pack(padx=10, pady=10)
            diff = cv2.absdiff(self.frame1,self.frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)

                if cv2.contourArea(contour) < 900:
                    continue
                cv2.rectangle(self.frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(self.frame1, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)
            frame1_resized = cv2.resize (self.frame1, (800, 700))
            self.out.write(frame1_resized)
            self.frame1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(self.frame1)
            img = ImageTk.PhotoImage(image=img)

            if self.video_label.winfo_exists():
                self.video_label.configure(image=img)
                self.video_label.image = img
            self.frame1 = self.frame2
            self.ret, self.frame2 = self.cap.read()
            if cv2.waitKey(25) & 0xFF == 27:
                break
        cv2.destroyAllWindows()
        self.cap.release()
        self.out.release()
        self.close()
    def close(self):
        self.root.destroy()

GUI()

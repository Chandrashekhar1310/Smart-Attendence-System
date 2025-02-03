import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.lang import Builder

import sqlite3
import qrcode

Builder.load_string('''
<QRPopup>:
    size_hint: None, None
    size: 400, 400
    auto_dismiss: False
    title: 'QR Code'
    BoxLayout:
        orientation: 'vertical'
        QRCode:
            id: qr
            size_hint: None, None
            size: 300, 300
        Button:
            text: 'OK'
            size_hint_y: None
            height: 50
            on_press: root.dismiss()
''')

class QRCode(Label):
    def __init__(self, text='', **kwargs):
        super(QRCode, self).__init__(**kwargs)
        self.text = text
        
    def on_text(self, instance, value):
        self.texture = self.generate_texture()
        
    def generate_texture(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(self.text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        return CoreImage(buf, ext='png').texture
        
class QRPopup(Popup):
    def __init__(self, qr_data, **kwargs):
        super().__init__(**kwargs)
        self.ids.qr.text = qr_data

class SmartAttendance(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        
        # Connect to database
        self.conn = sqlite3.connect('attendance.db')
        self.create_table()
        
        # Add widgets
        self.add_widget(Label(text="Smart Attendance", font_size=30))
        
        self.camera = Camera(play=True)
        self.add_widget(self.camera)
        
        capture_btn = Button(text="Capture QR code")
        capture_btn.bind(on_press=self.capture_qr)
        self.add_widget(capture_btn)
        
        self.attendance_label = Label(text="Attendance List", font_size=25)
        self.add_widget(self.attendance_label)
        
        get_attendance_btn = Button(text="Get Attendance List")
        get_attendance_btn.bind(on_press=self.get_attendance_list)
        self.add_widget(get_attendance_btn)
        
        self.attendance_list = Label(text="")
        self.add_widget(self.attendance_list)
        
    def create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS STUDENTS
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                             NAME TEXT NOT NULL,
                             ROLL_NUMBER INTEGER NOT NULL,
                             ATTENDANCE TEXT DEFAULT "Absent")''')
        
    def capture_qr(self, instance):
        # Capture QR code image
        qr_data = self.camera.export_to_png('qr.png')
        
        # Decode QR code
        decoded_qr_data = decode_qr(qr_data)
        
        # Update attendance
        if decoded_qr_data:
            stud_roll = decoded_qr_data
            self.conn.execute(f"UPDATE STUDENTS SET ATTENDANCE='Present' WHERE ROLL_NUMBER={stud_roll}")
            self.conn.commit()
            
            # Display QR code
            qr_popup = QRPopup(qr_data=f"Roll Number: {stud_roll}\nAttendance: Present")
            qr_popup.open()
            
            # Display updated attendance list
            self.get_attendance_list(instance)
            
        else:
            popup = Popup(title="Error", content=Label(text="QR code not detected"), size_hint=(None, None), size=(400, 200))
            popup.open()
    
    def get_attendance_list(self, instance):
        self.attendance_list.text = "Attendance List:\n"
        
        cursor = self.conn.execute("SELECT * FROM STUDENTS")
        for row in cursor:
            self.attendance_list.text += f"Name: {row[1]}\nRoll Number: {row[2]}\nAttendance: {row[3]}\n\n"
    
    def decode_qr(self, qr_data):
        qr = cv2.imread(qr_data)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(qr)
        if bbox is not None:
            return int(data)
        else:
            return None
            
class SmartAttendanceApp(App):
    def build(self):
        return SmartAttendance()
    
if __name__ == "__main__":
    SmartAttendanceApp().run()


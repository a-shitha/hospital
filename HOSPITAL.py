from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
import qrcode
from PIL import ImageTk, Image
import os
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class Hospital:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Hospital Management System")
        self.root.geometry("1600x800+0+0")
        self.root.config(bg="#f4f4f4")

        # Variables
        self.PatientName = StringVar()
        self.NHSnumber = StringVar()
        self.NamesofTablet = StringVar()
        self.dose = StringVar()
        self.daily_dose = StringVar()
        self.No_of_Tablet = StringVar()
        self.IssueDate = StringVar()
        self.ExpDate = StringVar()
        self.storage = StringVar()

        self.IssueDate.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="AshithaK",
                password="@shi123thaK",
                database="hospital_db"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Cannot connect: {e}")

        lblTitle = Label(self.root, text="🏥 Hospital Management System", font=("Arial", 30, "bold"), bg="#003366", fg="white", pady=10)
        lblTitle.pack(side=TOP, fill=X)

        DataFrame = Frame(self.root, bd=10, relief=RIDGE, padx=20, bg="white")
        DataFrame.place(x=10, y=80, width=1580, height=350)

        DataFrameLeft = LabelFrame(DataFrame, text="🩺 Patient Information", font=("Arial", 14, "bold"), bg="white", fg="#003366")
        DataFrameLeft.place(x=10, y=5, width=900, height=330)

        DataFrameRight = LabelFrame(DataFrame, text="📝 Prescription", font=("Arial", 14, "bold"), bg="white", fg="#003366")
        DataFrameRight.place(x=920, y=5, width=630, height=330)

        ButtonFrame = Frame(self.root, bd=10, relief=RIDGE, padx=20, bg="white")
        ButtonFrame.place(x=10, y=450, width=1580, height=80)

        DatabaseFrame = Frame(self.root, bd=10, relief=RIDGE, padx=20, bg="white")
        DatabaseFrame.place(x=10, y=540, width=1580, height=250)

        fields = [
            ("Patient Name", self.PatientName),
            ("NHS Number", self.NHSnumber),
            ("Tablet Name", self.NamesofTablet),
            ("Dose (mg)", self.dose),
            ("Daily Dose", self.daily_dose),
            ("No. of Tablets", self.No_of_Tablet),
            ("Issue Date", self.IssueDate),
            ("Exp Date", self.ExpDate),
            ("Storage Advice", self.storage),
        ]

        # Scrollable patient form
        scroll_container = Frame(DataFrameLeft, bg="white")
        scroll_container.place(x=10, y=10, width=570, height=300)

        canvas_left = Canvas(scroll_container, bg="white", highlightthickness=0)
        scrollable_frame_left = Frame(canvas_left, bg="white")
        canvas_left.create_window((0, 0), window=scrollable_frame_left, anchor="nw")

        def _on_mousewheel(event):
            canvas_left.yview_scroll(int(-1*(event.delta/120)), "units")

        scrollable_frame_left.bind(
            "<Configure>",
            lambda e: canvas_left.configure(
                scrollregion=canvas_left.bbox("all")
            )
        )

        canvas_left.pack(side=LEFT, fill=BOTH, expand=1)
        canvas_left.bind_all("<MouseWheel>", _on_mousewheel)
        canvas_left.configure(yscrollcommand=lambda *args: None)

        for i, (label, var) in enumerate(fields):
            lbl = Label(scrollable_frame_left, text=label + ":", font=("Arial", 12, "bold"), bg="white", fg="#333")
            lbl.grid(row=i, column=0, sticky=W, padx=10, pady=5)
            if label == "Tablet Name":
                tablet_options = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Metformin", "Aspirin"]
                comboTablet = ttk.Combobox(scrollable_frame_left, textvariable=var, values=tablet_options, font=("Arial", 12), width=33, state="readonly")
                comboTablet.grid(row=i, column=1, padx=10, pady=5)
            else:
                txt = Entry(scrollable_frame_left, textvariable=var, font=("Arial", 12), width=35, relief=RIDGE, bd=3)
                txt.grid(row=i, column=1, padx=10, pady=5)

        self.qr_label = Label(DataFrameLeft)
        self.qr_label.place(x=600, y=10, width=280, height=280)

        self.txtPrescription = Text(DataFrameRight, font=("Arial", 12), width=55, height=12, relief=RIDGE, bd=3)
        self.txtPrescription.pack(pady=5)

        columns = ("id", "name", "nhs", "tablet", "dose",  "num_tablets", "issue_date", "exp_date","daily_dose", "storage")
        self.patient_table = ttk.Treeview(DatabaseFrame, columns=columns, show="headings")

        for col in columns:
            self.patient_table.heading(col, text=col.replace("_", " ").title())
            self.patient_table.column(col, width=130, anchor=CENTER)

        self.patient_table.pack(fill=BOTH, expand=1)

        def fetch_data():
            try:
                self.cursor.execute("SELECT * FROM patients ORDER BY id")
                rows = self.cursor.fetchall()
                self.patient_table.delete(*self.patient_table.get_children())
                for row in rows:
                    self.patient_table.insert("", END, values=row)
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Error fetching data: {e}")

        def generate_prescription():
            self.txtPrescription.delete(1.0, END)
            prescription = f"""
Patient Name: {self.PatientName.get()}
Tablet Name: {self.NamesofTablet.get()}
Dose: {self.dose.get()} mg
Daily Dose: {self.daily_dose.get()} Times
No. of Tablets: {self.No_of_Tablet.get()}
Issue Date: {self.IssueDate.get()}
Exp Date: {self.ExpDate.get()}
Storage Advice: {self.storage.get()}
"""
            self.txtPrescription.insert(END, prescription)

        def add_record():
            try:
                sql = "INSERT INTO patients (patient_name, nhs_number, tablet_name, dose, daily_dose, num_tablets, issue_date, exp_date, storage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (
                    self.PatientName.get(),
                    self.NHSnumber.get(),
                    self.NamesofTablet.get(),
                    self.dose.get(),
                    self.daily_dose.get(),
                    self.No_of_Tablet.get(),
                    self.IssueDate.get(),
                    self.ExpDate.get(),
                    self.storage.get(),
                )
                self.cursor.execute(sql, values)
                self.db.commit()
                fetch_data()
                generate_prescription()
                messagebox.showinfo("Success", "Record Added Successfully")
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Error adding record: {e}")

        def update_record():
            selected = self.patient_table.focus()
            values = self.patient_table.item(selected, "values")
            if not values:
                messagebox.showerror("Error", "Select a record to update")
                return
            try:
                sql = "UPDATE patients SET patient_name=%s, nhs_number=%s, tablet_name=%s, dose=%s, daily_dose=%s, num_tablets=%s, issue_date=%s, exp_date=%s, storage=%s WHERE id=%s"
                self.cursor.execute(sql, (self.PatientName.get(), self.NHSnumber.get(), self.NamesofTablet.get(), self.dose.get(), self.daily_dose.get(), self.No_of_Tablet.get(), self.IssueDate.get(), self.ExpDate.get(), self.storage.get(), values[0]))
                self.db.commit()
                fetch_data()
                messagebox.showinfo("Success", "Record Updated Successfully")
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Error updating record: {e}")

        def delete_record():
            selected = self.patient_table.focus()
            values = self.patient_table.item(selected, "values")
            if not values:
                messagebox.showerror("Error", "Select a record to delete")
                return
            try:
                self.cursor.execute("DELETE FROM patients WHERE id=%s", (values[0],))
                self.db.commit()
                self.cursor.execute("SET @num := 0")
                self.cursor.execute("UPDATE patients SET id = @num := (@num + 1)")
                self.cursor.execute("ALTER TABLE patients AUTO_INCREMENT = 1")
                fetch_data()
                messagebox.showinfo("Success", "Record Deleted & ID Reset Successfully")
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Error deleting record: {e}")

        def generate_qr():
            prescription_text = self.txtPrescription.get(1.0, END)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4,
            )
            qr.add_data(prescription_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((280, 280), Image.Resampling.LANCZOS)
            img_path = "prescription_qr.png"
            img.save(img_path)
            try:
                self.qr_image = ImageTk.PhotoImage(Image.open(img_path))
                self.qr_label.config(image=self.qr_image)
                self.qr_label.image = self.qr_image
            except Exception as e:
                messagebox.showerror("Error", f"Failed to display QR code: {e}")

        def generate_pdf():
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                try:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    textobject = c.beginText(50, 750)
                    textobject.setFont("Helvetica", 12)
                    prescription_text = self.txtPrescription.get(1.0, END)
                    for line in prescription_text.split("\n"):
                        textobject.textLine(line)
                    c.drawText(textobject)
                    c.save()
                    messagebox.showinfo("Success", "Prescription saved as PDF")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save PDF: {e}")

        for text, command in [("Add", add_record), ("Update", update_record), ("Delete", delete_record), ("QR", generate_qr), ("PDF", generate_pdf), ("Exit", root.quit)]:
            Button(
                ButtonFrame, text=text, command=command,
                font=("Arial", 12, "bold"),
                bg="#0055aa", fg="white",
                activebackground="#007acc", activeforeground="white",
                width=12, height=2, relief=RAISED, bd=3
            ).pack(side=LEFT, padx=15, pady=5)

        fetch_data()

root = Tk()
obj = Hospital(root)
root.mainloop()

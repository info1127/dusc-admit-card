
# Streamlit version of the Tkinter-based Admit Card Generator
# Make sure to install: pip install streamlit pandas fpdf

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import tempfile

class AdmitCardPDF(FPDF):
    def __init__(self, exam_name, logo_path):
        super().__init__()
        self.exam_name = exam_name
        self.logo_path = logo_path
        self.set_auto_page_break(auto=False)

    def generate_card(self, student, y):
        outer_x = 10
        outer_y = y
        outer_w = 190
        outer_h = 85

        inner_margin = 3
        inner_x = outer_x + inner_margin
        inner_y = outer_y + inner_margin
        inner_w = outer_w - (2 * inner_margin)
        inner_h = outer_h - (2 * inner_margin)

        self.set_draw_color(0, 100, 0)
        self.rect(x=outer_x, y=outer_y, w=outer_w, h=outer_h)

        self.set_fill_color(255, 255, 255)
        self.rect(x=inner_x, y=inner_y, w=inner_w, h=inner_h, style='F')

        self.set_y(inner_y + 5)

        if self.logo_path:
            self.image(self.logo_path, x=inner_x + 3, y=inner_y + 2, w=20)

        self.set_font("Times", "B", 16)
        school_name = "Daffodil University School & College"
        exam_title = self.exam_name
        admit_text = "Admit Card"

        text_width = self.get_string_width(school_name)
        self.set_x((self.w - text_width) / 2)
        self.cell(text_width, 10, school_name)

        self.ln(10)
        text_width = self.get_string_width(exam_title)
        self.set_x((self.w - text_width) / 2)
        self.cell(text_width, 10, exam_title)

        self.ln(10)
        self.set_font("Times", "", 12)
        text_width = self.get_string_width(admit_text)
        self.set_x((self.w - text_width) / 2)
        self.cell(text_width, 10, admit_text)

        self.ln(5)
        self.set_x(inner_x + 5)
        self.cell(0, 10, f"Name: {student['Name']}", ln=True)

        self.set_x(inner_x + 5)
        self.cell(95, 10, f"ID: {student['ID']}")
        self.cell(0, 10, f"Class: {student['Class']}", ln=True)

        self.set_x(inner_x + 5)
        self.cell(0, 10, "Accounts: __________________________         Principal: __________________________", ln=True, align="C")
        self.ln(2)

def generate_admit_cards(df, exam_name, logo_path):
    pdf = AdmitCardPDF(exam_name, logo_path)

    cards_per_page = 3
    card_height = 95
    card_count = 0

    for _, row in df.iterrows():
        if card_count % cards_per_page == 0:
            pdf.add_page()

        y_position = 10 + (card_count % cards_per_page) * card_height
        pdf.generate_card(row, y_position)
        card_count += 1

    output_path = os.path.join(tempfile.gettempdir(), "All_Admit_Cards.pdf")
    pdf.output(output_path)
    return output_path

# Streamlit UI
st.set_page_config(page_title="DUSC Admit Card Generator", layout="centered")
st.title("🎓 DUSC Admit Card Generator")
st.write("Developed by Md Shahriar Hasan Sabuj")

exam_name = st.text_input("📘 Enter Exam Name", value="Half Yearly Exam")
logo_file = st.file_uploader("📌 Upload School Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
data_file = st.file_uploader("📋 Upload Excel File (Name, Class, ID)", type=["xlsx"])

if st.button("🚀 Generate Admit Cards"):
    if not exam_name.strip():
        st.warning("Please enter an exam name.")
    elif not logo_file:
        st.warning("Please upload the school logo.")
    elif not data_file:
        st.warning("Please upload the student Excel file.")
    else:
        logo_temp_path = os.path.join(tempfile.gettempdir(), logo_file.name)
        with open(logo_temp_path, "wb") as f:
            f.write(logo_file.read())

        df = pd.read_excel(data_file)
        pdf_path = generate_admit_cards(df, exam_name, logo_temp_path)

        with open(pdf_path, "rb") as f:
            st.download_button(label="📥 Download Admit Cards (PDF)", data=f, file_name="All_Admit_Cards.pdf")

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import tempfile

# =========================
# PDF Class
# =========================
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

        # Outer Border
        self.set_draw_color(0, 100, 0)
        self.rect(outer_x, outer_y, outer_w, outer_h)

        # Inner White Box
        self.set_fill_color(255, 255, 255)
        self.rect(inner_x, inner_y, inner_w, inner_h, style="F")

        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=inner_x + 3, y=inner_y + 3, w=18)

        # School Name
        self.set_xy(inner_x, inner_y + 2)
        self.set_font("Times", "B", 16)
        self.cell(inner_w, 8,
                  "Daffodil University School & College",
                  align="C")

        # Exam Name
        self.ln(8)
        self.set_font("Times", "B", 14)
        self.cell(inner_w, 8, self.exam_name, align="C")

        # Admit Card Text
        self.ln(8)
        self.set_font("Times", "", 12)
        self.cell(inner_w, 8, "Admit Card", align="C")

        # Student Information
        self.ln(10)

        name = str(student.get("Name", ""))
        class_name = str(student.get("Class", ""))
        student_id = str(student.get("ID", ""))

        self.set_x(inner_x + 5)
        self.cell(0, 8, f"Name : {name}", ln=True)

        self.set_x(inner_x + 5)
        self.cell(90, 8, f"ID : {student_id}")
        self.cell(0, 8, f"Class : {class_name}", ln=True)

        self.ln(5)

        self.set_x(inner_x + 5)
        self.cell(
            0,
            8,
            "Accounts Signature: __________              Principal Signature: __________",
            align="C",
            ln=True
        )

# =========================
# Generate PDF
# =========================
def generate_admit_cards(df, exam_name, logo_path):

    pdf = AdmitCardPDF(exam_name, logo_path)

    cards_per_page = 3
    card_height = 95

    for index, (_, row) in enumerate(df.iterrows()):

        if index % cards_per_page == 0:
            pdf.add_page()

        y_position = 10 + (index % cards_per_page) * card_height
        pdf.generate_card(row, y_position)

    output_path = os.path.join(
        tempfile.gettempdir(),
        "All_Admit_Cards.pdf"
    )

    pdf.output(output_path)

    return output_path


# =========================
# Streamlit UI
# =========================

st.set_page_config(
    page_title="DUSC Admit Card Generator",
    layout="centered"
)

st.title("🎓 DUSC Admit Card Generator")
st.markdown("**Developed by Md Shahriar Hasan Sabuj**")

exam_name = st.text_input(
    "📘 Enter Exam Name",
    value="Half Yearly Examination"
)

logo_file = st.file_uploader(
    "📌 Upload School Logo",
    type=["png", "jpg", "jpeg"]
)

data_file = st.file_uploader(
    "📋 Upload Excel File",
    type=["xlsx"]
)

if st.button("🚀 Generate Admit Cards"):

    if not exam_name.strip():
        st.warning("Please enter exam name.")

    elif logo_file is None:
        st.warning("Please upload school logo.")

    elif data_file is None:
        st.warning("Please upload Excel file.")

    else:

        try:
            # Save Logo
            logo_extension = os.path.splitext(
                logo_file.name
            )[1]

            logo_temp_path = os.path.join(
                tempfile.gettempdir(),
                f"school_logo{logo_extension}"
            )

            with open(logo_temp_path, "wb") as f:
                f.write(logo_file.getbuffer())

            # Read Excel
            df = pd.read_excel(data_file)

            required_columns = ["Name", "Class", "ID"]

            missing_cols = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing_cols:
                st.error(
                    f"Excel file must contain columns: {', '.join(required_columns)}"
                )

            else:

                pdf_path = generate_admit_cards(
                    df,
                    exam_name,
                    logo_temp_path
                )

                with open(pdf_path, "rb") as pdf_file:

                    st.success(
                        f"Successfully generated {len(df)} admit cards!"
                    )

                    st.download_button(
                        label="📥 Download Admit Cards (PDF)",
                        data=pdf_file,
                        file_name="All_Admit_Cards.pdf",
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"Error: {str(e)}")

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import tempfile

# =========================

# PDF CLASS

# =========================

class AdmitCardPDF(FPDF):

```
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

    # Border
    self.set_draw_color(0, 100, 0)
    self.rect(outer_x, outer_y, outer_w, outer_h)

    # Inner White Box
    self.set_fill_color(255, 255, 255)
    self.rect(inner_x, inner_y, inner_w, inner_h, style='F')

    # =========================
    # HEADER
    # =========================

    self.set_y(inner_y + 5)

    # Logo
    if self.logo_path:
        self.image(
            self.logo_path,
            x=inner_x + 3,
            y=inner_y + 2,
            w=20
        )

    # School Name
    self.set_font("Times", "B", 16)

    school_name = "Daffodil University School & College"

    text_width = self.get_string_width(school_name)

    self.set_x((self.w - text_width) / 2)

    self.cell(text_width, 10, school_name)

    # Exam Name
    self.ln(10)

    self.set_font("Times", "B", 14)

    exam_title = self.exam_name

    text_width = self.get_string_width(exam_title)

    self.set_x((self.w - text_width) / 2)

    self.cell(text_width, 10, exam_title)

    # Admit Card Text
    self.ln(8)

    self.set_font("Times", "", 13)

    admit_text = "Admit Card"

    text_width = self.get_string_width(admit_text)

    self.set_x((self.w - text_width) / 2)

    self.cell(text_width, 10, admit_text)

    # =========================
    # STUDENT INFO
    # =========================

    self.ln(6)

    self.set_font("Times", "", 12)

    # Name
    self.set_x(inner_x + 5)

    self.cell(
        0,
        10,
        f"Name: {student['Name']}",
        ln=True
    )

    # Safe ID Handling
    student_id = ""

    if pd.notna(student['ID']):

        try:
            student_id = str(int(float(student['ID'])))

        except:
            student_id = str(student['ID'])

    # ID + Class
    self.set_x(inner_x + 5)

    self.cell(
        95,
        10,
        f"ID: {student_id}"
    )

    self.cell(
        0,
        10,
        f"Class: {student['Class']}",
        ln=True
    )

    # Signature Area
    self.ln(5)

    self.set_x(inner_x + 5)

    self.cell(
        0,
        10,
        "Accounts: _____________________      Principal: _____________________",
        ln=True,
        align="C"
    )
```

# =========================

# PDF GENERATOR FUNCTION

# =========================

def generate_admit_cards(df, exam_name, logo_path):

```
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

output_path = os.path.join(
    tempfile.gettempdir(),
    "All_Admit_Cards.pdf"
)

pdf.output(output_path)

return output_path
```

# =========================

# STREAMLIT UI

# =========================

st.set_page_config(
page_title="DUSC Admit Card Generator",
page_icon="🎓",
layout="centered"
)

# Title

st.markdown(
""" <h1 style='text-align:center; color:#0B6E4F;'>
🎓 DUSC Admit Card Generator </h1>

```
<h4 style='text-align:center; color:gray;'>
Daffodil University School & College
</h4>

<p style='text-align:center;'>
Generate professional admit cards instantly from Excel sheets.
</p>
""",
unsafe_allow_html=True
```

)

# Developer

st.markdown(
""" <div style='text-align:center; color:gray; font-size:14px;'>
Developed by <b>Md. Shahriar Hasan Sabuj</b> </div> <br>
""",
unsafe_allow_html=True
)

# =========================

# INPUTS

# =========================

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

# =========================

# PREVIEW EXCEL

# =========================

if data_file:

```
try:

    df = pd.read_excel(data_file)

    required_columns = ["Name", "Class", "ID"]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            f"❌ Missing Columns: {', '.join(missing_columns)}"
        )

    else:

        st.subheader("📋 Student Data Preview")

        st.dataframe(df)

        st.success(
            f"✅ Total Students: {len(df)}"
        )

except Exception as e:

    st.error(
        f"❌ Error Reading Excel File: {e}"
    )
```

# =========================

# GENERATE BUTTON

# =========================

if st.button("🚀 Generate Admit Cards"):

```
if not exam_name.strip():

    st.warning(
        "⚠ Please enter exam name."
    )

elif not logo_file:

    st.warning(
        "⚠ Please upload school logo."
    )

elif not data_file:

    st.warning(
        "⚠ Please upload Excel file."
    )

else:

    try:

        # Save Logo
        logo_temp_path = os.path.join(
            tempfile.gettempdir(),
            logo_file.name
        )

        with open(logo_temp_path, "wb") as f:

            f.write(
                logo_file.read()
            )

        # Read Excel
        df = pd.read_excel(data_file)

        # Generate PDF
        pdf_path = generate_admit_cards(
            df,
            exam_name,
            logo_temp_path
        )

        st.success(
            "✅ Admit Cards Generated Successfully!"
        )

        # Download Button
        with open(pdf_path, "rb") as f:

            st.download_button(
                label="📥 Download Admit Cards PDF",
                data=f,
                file_name="All_Admit_Cards.pdf",
                mime="application/pdf"
            )

    except Exception as e:

        st.error(
            f"❌ Error: {e}"
        )
```

# =========================

# FOOTER

# =========================

st.markdown(
""" <hr>

```
<div style='text-align:center; color:gray; font-size:13px;'>

DUSC Automation System <br>
© 2026 Daffodil University School & College

</div>
""",
unsafe_allow_html=True
```

)

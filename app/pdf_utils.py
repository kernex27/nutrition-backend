from fpdf import FPDF
from datetime import datetime

def generate_pdf(consumptions, totals, username):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Judul
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Laporan Konsumsi Makanan", ln=True, align="C")
    pdf.ln(10)

    # Nama pengguna dan tanggal
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Pengguna: {username}", ln=True)
    pdf.cell(200, 10, txt=f"Tanggal laporan: {datetime.now().strftime('%d %B %Y %H:%M')}", ln=True)
    pdf.ln(10)

    # Header tabel
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(30, 10, "Tanggal", 1)
    pdf.cell(20, 10, "Jam", 1)
    pdf.cell(40, 10, "Makanan", 1)
    pdf.cell(25, 10, "Berat (g)", 1)
    pdf.cell(20, 10, "Kalori", 1)
    pdf.cell(20, 10, "Protein", 1)
    pdf.cell(20, 10, "Karbo", 1)
    pdf.cell(20, 10, "Lemak", 1)
    pdf.ln()

    pdf.set_font("Arial", size=10)

    # Isi tabel
    for c in consumptions:
        pdf.cell(30, 10, c.eaten_at.strftime('%d %b %Y'), 1)
        pdf.cell(20, 10, c.eaten_at.strftime('%H:%M'), 1)
        pdf.cell(40, 10, c.food.name, 1)
        pdf.cell(25, 10, f"{c.weight_g} g", 1)
        pdf.cell(20, 10, f"{c.kcal:.0f}", 1)
        pdf.cell(20, 10, f"{c.protein_g:.1f}", 1)
        pdf.cell(20, 10, f"{c.carbs_g:.1f}", 1)
        pdf.cell(20, 10, f"{c.fat_g:.1f}", 1)
        pdf.ln()

    pdf.ln(10)

    # Ringkasan total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Ringkasan Nutrisi", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(50, 10, f"Total Kalori : {totals['kcal']:.0f} kcal", ln=True)
    pdf.cell(50, 10, f"Total Protein: {totals['protein_g']:.1f} g", ln=True)
    pdf.cell(50, 10, f"Total Karbo  : {totals['carbs_g']:.1f} g", ln=True)
    pdf.cell(50, 10, f"Total Lemak  : {totals['fat_g']:.1f} g", ln=True)

    # Simpan file PDF
    filename = f"laporan_konsumsi_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)

    return filename

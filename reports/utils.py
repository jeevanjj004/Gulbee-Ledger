from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import openpyxl
from io import BytesIO


# ---------- PDF ----------
def render_to_pdf(template_src, context):
    html = render_to_string(template_src, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if pdf.err:
        return HttpResponse("Error generating PDF", status=500)

    return HttpResponse(result.getvalue(), content_type="application/pdf")


# ---------- EXCEL ----------
def export_to_excel(data, filename, columns):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Report"

    ws.append(columns)

    for row in data:
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename={filename}.xlsx"
    return response

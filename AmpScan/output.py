from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from reportlab.pdfgen import canvas
import io

def getPDF(lngths, perimeters):
    """
    creates a PDF file containing information about the mesh
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet)
    for i in range(1, len(lngths)-1):
        stringl = "{}".format(int(lngths[i]))
        stringp = "{}".format(int(perimeters[i]))
        c.drawString(90, 495- ((i-1)*75), stringl)
        c.drawString(170, 495- ((i-1)*75), stringp)
    stringmaxZ = "{}".format(int(lngths[len(lngths)-1]))
    c.drawString(495, 420, stringmaxZ)
    c.save()
    packet.seek(0)
    newpdf = PdfFileReader(packet)
    template = PdfFileReader(open("Measurements2.pdf", "rb"))
    output = PdfFileWriter()
    page = template.getPage(0)
    page.mergePage(newpdf.getPage(0))
    output.addPage(page)
    outputStream = open("Output.pdf", "wb")
    output.write(outputStream)
    outputStream.close
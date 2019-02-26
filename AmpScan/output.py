from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from reportlab.pdfgen import canvas
import io

def getPDF(lngths, perimeters, CSA,APW,MLW):
    """
    creates a PDF file containing information about the limb
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet)
    for i in range(1, len(lngths)-1):
        stringl = "{}".format(round(lngths[i],1))
        stringp = "{}".format(round(perimeters[i],1))
        c.drawString(360+((i-1)*27), 474-((i-1)*41.5), stringl)
        c.drawString(88, 524.5- ((i-1)*74.5), stringp)
    stringmaxZ = "{}".format(int(lngths[len(lngths)-1]))
    c.drawString(514, 419, stringmaxZ)
    c.setFont("Courier-Bold", 12)
    c.drawString(65, 575, "Perimeter / cm")
    c.drawString(400, 520, "Distance / cm")
    c.showPage()
    c.drawImage("ant.png", 38,225, 256,256)
    c.drawImage("lat.png", 300,225,256,256)
    c.drawImage("figure.png", 35,-80, 256,256)
    for i in range(1,len(CSA),2):
        sCSA = "{}".format(round(CSA[i],1))
        sAPW = "{}".format(round(APW[i],2))
        sMLW = "{}".format(round(MLW[i],2))
        c.drawString(408, 145-((i-1)*11.5), sCSA)
        c.drawString(465, 145-((i-1)*11.5), sAPW)
        c.drawString(520, 145-((i-1)*11.5), sMLW)
    c.save()
    packet.seek(0)
    newpdf = PdfFileReader(packet)
    template = PdfFileReader(open("Measurements2.pdf", "rb"))
    t2 = PdfFileReader(open("Output Template.pdf", "rb"))
    output = PdfFileWriter()
    page = t2.getPage(0)
    page.mergePage(newpdf.getPage(1))
    page2 = template.getPage(0)
    page2.mergePage(newpdf.getPage(0))
    output.addPage(page)
    output.addPage(page2)
    outputStream = open("Output.pdf", "wb")
    output.write(outputStream)
    outputStream.close
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
import io
import os
import csv


def getPDF(lngths, perimeters, CSA, APW, MLW):
    """
    creates a PDF file containing information about the limb in correct
    locations on the page
    then merges the PDF file with the existing template to create the output
    file

    Returns
    -------
    The file path to the PDF
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet)
    for i in range(1, len(lngths)-1):
        stringl = "{}".format(abs(round(lngths[i],1)))
        stringp = "{}".format(abs(round(perimeters[i],1)))
        c.drawString(360+((i-1)*27), 474-((i-1)*41.5), stringl)
        c.drawString(88, 524.5- ((i-1)*74.5), stringp)
    stringmaxZ = "{}".format(abs(round(lngths[len(lngths)-1],1)))
    c.drawString(514, 419, stringmaxZ)
    c.setFont("Courier-Bold", 12)
    c.drawString(65, 575, "Perimeter / cm")
    c.drawString(400, 520, "Distance / cm")
    c.showPage()
    c.drawImage("ant.png", 38,225, 256,256)
    c.drawImage("lat.png", 300,225,256,256)
    c.drawImage("figure.png", -2.5,-50, 334,200)
    for i in range(1,len(CSA),2):
        sCSA = "{}".format(round(CSA[i],1))
        sAPW = "{}".format(round(APW[i],1))
        sMLW = "{}".format(round(MLW[i],1))
        c.drawString(403, 145-((i-1)*11.5), sCSA)
        c.drawString(465, 145-((i-1)*11.5), sAPW)
        c.drawString(520, 145-((i-1)*11.5), sMLW)
    c.save()
    packet.seek(0)
    newpdf = PdfFileReader(packet)
    template = PdfFileReader(open(os.path.join("res", "Measurements Template.pdf"), "rb"))
    t2 = PdfFileReader(open(os.path.join("res", "Output Template.pdf"), "rb"))
    output = PdfFileWriter()
    page = t2.getPage(0)
    page.mergePage(newpdf.getPage(1))
    page2 = template.getPage(0)
    page2.mergePage(newpdf.getPage(0))
    output.addPage(page)
    output.addPage(page2)

    output_file_path = os.path.join(get_downloads_folder(), "AmpScanReport.pdf")
    outputStream = open(output_file_path, "wb")
    output.write(outputStream)

    outputStream.close()

    return output_file_path


def get_downloads_folder():
    """Gets the downloads folder in a relatively platform independent way"""

    # Get user dir
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads_path):  # If downloads folder doesn't exist, create it
        os.mkdir(downloads_path)

    return downloads_path


def generateRegBinsCsv(file, regObject, numBins, scalarMin, scalarMax):
    """
    Generates a CSV file output of scalar values put into bins
    :param file: The open file to save csv output to. Should be open with newline=''
    :param regObject: The reg object with scalar values
    :param numBins: Number of bins for scalar values
    :param scalarMin: The min scalar value to look for
    :param scalarMax: The max scalar value to look for
    :return: None
    """
    writer = csv.writer(file)

    binSize = (scalarMax - scalarMin) / numBins
    bins = []
    binValues = []
    for i in range(numBins):
        binValues.append(scalarMin + binSize * i)
        bins.append(0)
    for point in regObject.values:
        bin = int((point - scalarMin) / binSize)
        if bin < 0:
            bins[0] += 1
        elif bin >= len(bins):
            bins[-1] += 1
        else:
            bins[bin] += 1
    l = len(regObject.values)

    for i in range(numBins):
        writer.writerow([scalarMin+binSize*i, bins[i] / l])


def generateRegCsv(file, regObject):
    """
    Generates a CSV file output of scalar values put into bins
    :param file: The open file to save csv output to. Should be open with newline=''
    :param regObject: The reg object with scalar values
    :return: None
    """
    writer = csv.writer(file)
    for i in regObject.values:
        writer.writerow(i)


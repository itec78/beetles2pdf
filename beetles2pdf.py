from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from io import BytesIO
from PIL import Image
import os

import qrcode
from fpdf import FPDF

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1000,800")
chrome_options.add_argument("--force-device-scale-factor=4.0")

driver = webdriver.Chrome(options=chrome_options)
os.makedirs('out', exist_ok=True)

for x in range(0, 2000):
    fname = os.path.join("out","beetle%s.pdf" % (str(x).zfill(4)))
    print(fname)
    if not os.path.isfile(fname):
        driver.get("http://localhost:8080/") #on local, otherwise you should use the main site https://beetles.bleeptrack.de/

        # reads name and link
        name = driver.find_element(By.ID, "name").get_attribute('innerText')
        seed = driver.find_element(By.ID, "permalink").get_attribute('innerText')

        # image = driver.find_element(By.ID, "beetle").screenshot_as_png
        # # image = driver.get_screenshot_as_png()
        # imageStream = BytesIO(image)
        # im = Image.open(imageStream)
        # im.save("antani.png")
        # driver.quit()
        
        # Do a screenshot to extract the image. Chormium is needed
        driver.execute_script("document.body.style.zoom = '50%'")
        element = driver.find_element(By.ID, "beetle")
        location = element.location
        size = element.size
        png = driver.get_screenshot_as_png() # saves screenshot of entire page

        im = Image.open(BytesIO(png)) # uses PIL library to open image in memory

        left = location['x'] * 2 # must mutliply all these numbers by your zoom
        top = location['y'] * 2
        right = (location['x'] + size['width']) * 2
        bottom = (location['y'] + size['height']) * 2

        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save("/tmp/beetle.png") # saves new cropped image


        # Creates the qr code
        img = qrcode.make(seed)
        type(img)  # qrcode.image.pil.PilImage
        img.save("/tmp/qr.png")


        # Compose the page
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()

        w = 180
        pdf.image("/tmp/beetle.png",w=w, x=(210-w)/2, y=20)


        pdf.set_xy((210-w)/2, 150)
        pdf.set_font('Times', '', 40)
        pdf.set_text_color(68, 68, 68)
        pdf.multi_cell(w=w, h=20.0, align='C', txt=",\n".join(name.split(", ")), border=0)

        w = 60
        pdf.image("/tmp/qr.png",w=w, x=(210-w)/2, y=200)

        w = 180
        pdf.set_xy((210-w)/2, 275)
        pdf.set_font('Times', '', 16)
        pdf.set_text_color(68, 68, 68)
        pdf.cell(w=w, align='C', txt="Bugs & Beetles by bleeptrack - https://bleeptrack.de/projects/beetlesbot/", border=0)

        pdf.output(fname,'F')

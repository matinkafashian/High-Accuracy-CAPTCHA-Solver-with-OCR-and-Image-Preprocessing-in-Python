from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import pytesseract
import numpy as np
import re

driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get("https://bahmancustomer.iranecar.com/BranchLogin.aspx?s=acd53f8f-8c0a-4227-ba16-1eadd04e02cb")

captcha = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//img[contains(@src, "captcha.aspx")]')))
captcha.screenshot('captcha.png')

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image = cv2.imread('captcha.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
kernel = np.ones((2, 2), np.uint8)
morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

def ocr_attempt(img, config):
    result = pytesseract.image_to_string(img, config=config)
    result = re.sub(r'[^A-Z]', '', result.upper())
    return result

config1 = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
config2 = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'

text = ocr_attempt(morph, config1)

if len(text) != 5:
    alt = ocr_attempt(morph, config2)
    if len(alt) == 5:
        text = alt
    elif len(text) > 5:
        text = text[:5]
    elif len(text) < 5 and len(alt) > len(text):
        text = alt[:5]

if len(text) == 5:
    print("✅ Captcha:", text)
    textbox = driver.find_elements(By.CLASS_NAME, 'textbox')
    textbox[2].send_keys(text)
else:
    print("❌wrong captcha - ", text)


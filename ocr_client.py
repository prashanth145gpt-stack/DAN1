 
import requests, json
 
# OCR_ENDPOINT = "https://file-extractordev.sidbi.in/extract"
# OCR_ENDPOINT = "http://172.30.1.200:7002/pdf-ocr-extractor/extract-ocr" # for docker
#OCR_ENDPOINT = "https://file-extractordev.sidbi.in/pdf-ocr-extractor/extract-ocr" # in sidbi laptop
OCR_ENDPOINT = "http://172.30.1.200:7002/extract-ocr"

 
# def send_to_ocr(pdf_bytes):
#     files = {
#         "file":("page.pdf", pdf_bytes,"application/pdf")
#     }
 
#     resp = requests.post(OCR_ENDPOINT, files=files)
#     if resp.status_code != 200:
#         return ""
#     print(type(resp))
#     data = resp.json()
#     return json.dumps(data,indent=2)

def send_to_ocr(pdf_bytes):
    files = {
        "file":("page.pdf", pdf_bytes,"application/pdf")
    }

    resp = requests.post(OCR_ENDPOINT, files=files,timeout=6000,
                    proxies= {"http":None, "https":None})
    if resp.status_code == 200:
        data = resp.json()
        return json.dumps(data,indent=2)
    else:
        print("OCR FAILED: ", resp.status_code,resp.text)
        return "OCR Failed"
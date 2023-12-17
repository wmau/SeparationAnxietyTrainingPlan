import gspread
from gspread_dataframe import set_with_dataframe

gc = gspread.service_account(r"C:\Users\Wackie\Desktop\Kewpie\true-alliance-408420-3fa666e4c05f.json")

class WriteMission:
    def __init__(self, url):
        self.gc = gc
        self.url = url
        self.sh = gc.open_by_url(self.url)

    def get_sheet(self, sheet_name):

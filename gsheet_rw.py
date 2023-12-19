import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from gspread_formatting import set_column_width
import matplotlib.pyplot as plt

gc = gspread.service_account(
    r"C:\Users\Wackie\Desktop\Kewpie\true-alliance-408420-3fa666e4c05f.json"
)
url = "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=0"


class WriteMission:
    def __init__(self, url):
        self.gc = gc
        self.url = url
        self.sh = self.gc.open_by_url(self.url)

    def get_worksheet(self, sheet_name):
        try:
            wks = self.sh.worksheet(sheet_name)
        except:
            wks = self.sh.add_worksheet(title=sheet_name, rows=40, cols=5)

        return wks

    def populate_sheet(self, wk, df):
        self.write_df(wk, df)
        self.add_comma_counter(wk, df)

    def write_df(self, wk, df):
        set_with_dataframe(wk, df, 1, 1)
        set_column_width(wk, "D", 650)

    def add_comma_counter(self, wk, df):
        wk.update("E1", "comma_count")
        table_len = len(df)
        wk.update(
            f"E2:E{table_len+2}",
            [
                [f'=len(D{i})-len(SUBSTITUTE(D{i},",",""))+1']
                for i in range(2, table_len + 2)
            ],
            raw=False,
        )


class ReadEthogram:
    def __init__(self, url, date):
        self.gc = gc
        self.url = url
        self.date = date
        self.sh = self.gc.open_by_url(self.url)

    def run(self):
        wks = self.get_sheet(self.date)
        df = self.get_df(wks)
        df = self.clean_df(df)

        return df

    def get_sheet(self, sheet_name):
        wks = self.sh.worksheet(sheet_name)

        return wks

    def get_df(self, wks):
        df = get_as_dataframe(wks)

        return df

    def clean_df(self, df):
        df = df.query("type == 'departure'")
        df["ethogram"] = df["ethogram"].str.split(",")
        df = df.explode("ethogram")
        df["observation"] = range(len(df))

        return df


class EthogramVisualizer:
    def __init__(self, df):
        self.df = df
        self.abbrev_dict = {""}

    def plot(self):
        fig, ax = plt.subplots()
        ax.scatter(self.df["observation"], self.df["ethogram"], marker="|")
        ax.set_xlabel("Observation")
        ax.set_ylabel("Behavior")


if __name__ == "__main__":
    E = ReadEthogram(
        "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=760727155",
        "2023-12-17",
    )
    df = E.run()

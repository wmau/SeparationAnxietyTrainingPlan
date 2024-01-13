import gspread
import gspread_dataframe
import gspread_formatting
import utils

gc = gspread.service_account(
    r"C:\Users\Wackie\Desktop\Kewpie\true-alliance-408420-3fa666e4c05f.json"
)
url = "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=0"

ethogram_dictionary = {
    "A": "Away",
    "L": "Lying",
    "Ld": "Lying @ door",
    "PL": "Playing",
    "RH": "Resting head",
    "SI": "Sitting",
    "SId": "Sitting @ door",
    "ST": "Stretching",
    "Sd": "Standing @ door",
    "S": "Standing",
    "SC": "Scratching self",
    "W": "Walking",
    "SN": "Sniffing",
    "PW": "Pawing @ door",
    "G": "Growling",
    "P": "Pacing",
    "BO": "Bork",
    "B": "Bark!",
    "BB": "Big bark!!",
}

class MissionWriter:
    def __init__(self, url):
        """
        Open a Google Sheet, find the appropriate worksheet, and write a dataframe
        (mission).

        Parameter
        ---
        url: str
            URL to the Google Sheet.

        """
        self.gc = gc
        self.url = url
        self.sh = self.gc.open_by_url(self.url)

    def get_worksheet(self, sheet_name="Data"):
        try:
            wks = self.sh.worksheet(sheet_name)
            self.is_new_page = False
        except:
            wks = self.sh.add_worksheet(title=sheet_name, rows=2000, cols=6)
            gspread_formatting.set_column_width(wks, "E", 650)
            self.add_comma_counter(wks)

            self.is_new_page = True

        return wks

    def populate_sheet(self, wk, df, start_index):
        self.write_df(wk, df, start_index)
        self.add_comma_counter(wk)

    def write_df(self, wk, df, start_index):
        gspread_dataframe.set_with_dataframe(
            wk, df, row=start_index, col=1, include_column_header=self.is_new_page
        )

    def add_comma_counter(self, wk):
        """
        Add a column that shows the number of commas in column E.
        Column E is the column containing ethogram labels which are
        comma-separated. Since we are counting one behavior per second,
        this column helps us ensure the number of observations matches the
        number of seconds in the departure.

        :parameters
        ---
        wk: Worksheet object

        df: pandas DataFrame
            Mission df. Only needed to find the range of the column logic.
        """
        wk.update("F1", "comma_count")
        wk.update(
            f"F2:F2000",
            [[f'=len(E{i})-len(SUBSTITUTE(E{i},",",""))+1'] for i in range(2, 2000)],
            raw=False,
        )


class EthogramReader:
    def __init__(self, url, worksheet_name):
        """
        Read the ethogram column in the Google Sheet and explode the comma-separated
        values into individual rows to create a long-form dataframe.

        url: str
            URL of the Google Sheet.

        date: str
            Really the worksheet name.
        """
        self.gc = gc
        self.url = url
        self.worksheet_name = worksheet_name
        self.sh = self.gc.open_by_url(self.url)
        self.wks = self.sh.worksheet(self.worksheet_name)

    def run(self, explode_ethogram=True):
        df = utils.get_as_dataframe(self.wks)

        if explode_ethogram:
            df = self.explode_ethogram(df)

        return df.drop(columns="comma_count")

    def explode_ethogram(self, df):
        """
        Preprocesses the dataframe for plotting:
        -Filters for departure rows only.
        -Split comma-separated values and explode.
        -Add an 'observations' column which is just an index.
        -Replace the ethogram behavior abbreviation with the full word.
            -Note this gets replaced again by an integer in EthogramVisualizer.

        :param df:
        :return:
        """
        df = df.query("type == 'departure'")
        df["ethogram"] = df["ethogram"].str.split(",")
        df = df.explode("ethogram")
        df["observation"] = range(len(df))
        df["ethogram"] = df["ethogram"].replace(ethogram_dictionary)

        return df.reset_index(drop=True)


if __name__ == "__main__":
    from main import ReadPipeline

    R = ReadPipeline()
    df = R.read(explode_ethogram=True)

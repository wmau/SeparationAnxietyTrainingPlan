from mission_control import MissionGenerator
from gsheet_rw import MissionWriter, EthogramReader, gc
import datetime
import gspread_dataframe

url = "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=0"

def get_as_dataframe(wks):
    df = gspread_dataframe.get_as_dataframe(wks)

    # This line matches the df indices to the row numbers on Gsheets.
    # GSheet is not 0-indexed, so we add one.
    # Reading it in as a df makes the first row the header so we "lose" a row.
    df.index = df.index + 2

    return df

class WritePipeline:
    def __init__(
        self,
        first_departure_duration,
        last_departure_duration,
        date=None,
        mission_duration=1200,
        noise_factor=0.5,
        url=url,
    ):
        """
        Strings together the mission generator pipeline and the mission writer
        pipeline.

        """
        if date is None:
            date = str(datetime.datetime.now().date())
        if isinstance(date, datetime.datetime):
            date = str(date)
        self.date = date

        self.M = MissionGenerator(
            first_departure_duration,
            last_departure_duration,
            noise_factor=noise_factor,
            date=self.date,
            mission_duration=mission_duration,
        )

        self.GS = MissionWriter(url)
        self.wks = self.GS.get_worksheet()

    def run(self):
        # Delete today's mission if any exist.
        self.delete_today()

        # Append today's mission.
        self.append_mission()

    def append_mission(self):
        mission = self.M.generate_mission()

        df = get_as_dataframe(self.wks)
        start_index = df.index[df.iloc[:,:1].isnull().all(axis=1)][0]

        self.GS.populate_sheet(self.wks, mission, start_index)

    def delete_today(self):
        """
        Find any existing rows where date is today and delete.

        :param wks: Worksheet object
        :return:
        """
        # Read worksheet in as dataframe.
        df = get_as_dataframe(self.wks)

        # Find rows for today's date.
        rows = df.index[df["date"] == self.date]

        if not rows.empty:
            start_index = int(rows[0])
            end_index = int(rows[-1])

            # Delete.
            self.wks.delete_rows(start_index, end_index)


class ReadPipeline:
    def __init__(self, url, dates="all"):
        self.url = url
        self.gc = gc
        self.sh = self.gc.open_by_url(self.url)

        if dates == "all":
            self.dates = [worksheet.title for worksheet in self.sh.worksheets()]
        else:
            self.dates = dates

    def read_worksheets(self):
        df_list = [EthogramReader(url, date).run() for date in self.dates]

        return df_list

    def read_worksheets_condensed(self):
        df_list = [
            EthogramReader(url, date).run(explode_ethogram=False) for date in self.dates
        ]

        return df_list

if __name__ == "__main__":
    P = WritePipeline(16, 80, noise_factor=0.5)
    P.run()

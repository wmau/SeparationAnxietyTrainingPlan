import gspread_dataframe


def get_as_dataframe(wks):
    df = gspread_dataframe.get_as_dataframe(wks)

    # This line matches the df indices to the row numbers on Gsheets.
    # GSheet is not 0-indexed, so we add one.
    # Reading it in as a df makes the first row the header so we "lose" a row.
    df.index = df.index + 2

    return df


def get_session_dates(df):
    date_changes = df.index[df["date"] != df["date"].shift(1)].tolist()
    df = df.loc[date_changes]

    return df

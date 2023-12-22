import numpy as np
import pandas as pd
import datetime


class Mission:
    def __init__(
        self,
        first_departure_duration,
        last_departure_duration,
        noise_factor=0.5,
        date=None,
    ):
        """

        :param first_departure_duration:
        :param last_departure_duration:
        :param noise_factor:
        :param date:
        """
        self.first_departure_duration = first_departure_duration
        self.last_departure_duration = last_departure_duration
        self.noise_factor = noise_factor
        if date is None:
            date = datetime.datetime.now().date()
        self.date = date

        self.rest_intervals = [30, 90]
        self.mission_duration = 1200
        self.departure_count = int(
            np.floor(
                self.mission_duration
                / (
                    np.mean(
                        [self.first_departure_duration, self.last_departure_duration]
                    )
                    + np.mean(self.rest_intervals)
                )
            )
        )

    def generate_mission(self):
        rest_intervals = self.generate_rest_intervals()
        departures = self.generate_departures()

        mission = np.empty(
            rest_intervals.size + departures.size, dtype=rest_intervals.dtype
        )
        mission[::2] = departures
        mission[1::2] = rest_intervals

        mission_df = pd.DataFrame(
            {
                "date": self.date,
                "type": ["departure", "rest"] * int(len(mission) / 2),
                "triggers": None,  # placeholder for triggers TODO
                "durations": mission,
                "ethogram": None,
            }
        )
        mission_df.drop(mission_df.tail(1).index, inplace=True)

        return mission_df

    def generate_rest_intervals(self):
        rest_intervals = np.random.randint(
            *self.rest_intervals, size=self.departure_count
        )

        return rest_intervals

    def generate_departures(self):
        departures_ = np.linspace(
            self.first_departure_duration,
            self.last_departure_duration,
            self.departure_count,
        )

        departures = []
        for departure in departures_:
            temp = departure + np.random.randint(-self.noise_factor * departure, 0)
            new_value = 10 if temp < 10 else temp

            departures.append(new_value)
        departures[-1] = self.last_departure_duration

        return np.array(departures)


if __name__ == "__main__":
    M = Mission(10, 40, 0.8)
    M.generate_mission()

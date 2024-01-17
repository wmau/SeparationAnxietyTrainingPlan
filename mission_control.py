import numpy as np
import pandas as pd
import datetime

possible_triggers = {
    "keys": 0.3,
    "coat": 0.2,
    "shoes": 0.2,
}


class MissionGenerator:
    def __init__(
        self,
        first_departure_duration,
        last_departure_duration,
        noise_factor=0.5,
        date=None,
        mission_duration=1200,
        add_triggers=True,
    ):
        """
        Create a day's mission. A mission has these characteristics:
        -20-30 min long.
        -A globally ramping duration in departures.
        -Locally semi-stochastic departure durations to allow for 'easy wins'.
        -Variable rest periods between 30-90 s (pulled from a uniform distribution).
        -The last departure is the longest.

        Parameters
        ---
        first_departure_duration: int
            Lower bound of departure durations, in seconds.

        last_departure_duration: int
            Upper bound of departure durations (last departure), in seconds.

        noise_factor: float
            From 0-1. For each departure, get x_i from a step function ranging
            from first_departure_duration to last_departure_duration. Then pull from
            a uniform distribution ranging from 0 to noise_factor * x_i and call that
            value z_i. The final duration for that departure i is x_i - z_i.

        date: str, datetime.datetime object, or None
            Date to write to dataframe.

        mission_duration: int
            Length of mission in seconds. Usually 1200 (20 min, but flexible).
        """
        self.first_departure_duration = first_departure_duration
        self.last_departure_duration = last_departure_duration
        self.noise_factor = noise_factor
        if date is None:
            date = datetime.datetime.now().date()
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.date = date

        self.rest_intervals = [30, 90]  # seconds
        self.mission_duration = mission_duration  # seconds
        self.add_triggers = add_triggers

        # Create n departures that would fit in a 20-30 min mission given the
        # departure durations.
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
        if self.add_triggers:
            temp = self.generate_triggers()
            triggers = [item for sublist in zip(temp, [""]*(len(temp))) for item in sublist]
        else:
            triggers = False

        # Interleave departures with rest periods.
        mission = np.empty(
            rest_intervals.size + departures.size, dtype=rest_intervals.dtype
        )
        mission[::2] = departures
        mission[1::2] = rest_intervals


        mission_df = pd.DataFrame(
            {
                "date": str(self.date),
                "type": ["departure", "rest"] * int(len(mission) / 2),
                "triggers": triggers,
                "durations": mission,
                "ethogram": None,  # placeholder for manually recorded behaviors
            }
        )
        mission_df.drop(
            mission_df.tail(1).index, inplace=True
        )  # Don't need last rest period.

        return mission_df

    def generate_rest_intervals(self):
        # Draw a random rest period from a uniform distribution of [30, 90]
        rest_intervals = np.random.randint(
            *self.rest_intervals, size=self.departure_count
        )

        return rest_intervals

    def generate_departures(self):
        # Generate step function (ramping departure durations).
        departures_ = np.linspace(
            self.first_departure_duration,
            self.last_departure_duration,
            self.departure_count,
        )

        # For each departure, subtract a pseudorandom value.
        departures = []
        for departure in departures_:
            temp = round(departure * np.random.uniform(self.noise_factor, 1))
            new_value = (
                self.first_departure_duration
                if temp < self.first_departure_duration
                else temp
            )

            departures.append(new_value)
        departures[
            -1
        ] = self.last_departure_duration  # Last departure is always the longest.

        return np.array(departures)

    def generate_triggers(self):
        r = np.random.sample(size=(self.departure_count, len(possible_triggers)))
        r = pd.DataFrame(r, columns=possible_triggers.keys())

        for trigger, threshold in possible_triggers.items():
            r[trigger] = r[trigger] < threshold

        r["triggers"] = r.apply(lambda x: ",".join(r.columns[x]), axis=1)

        return r["triggers"].tolist()


if __name__ == "__main__":
    M = MissionGenerator(10, 40, noise_factor=0.8)
    mission_df = M.generate_mission()

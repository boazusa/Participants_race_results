class RaceResultEngine:
    def __init__(self, api: RaceViewAPI):
        self.api = api

    def get_best_result(self, runner_name: str, category: str, years_back: int = 5):
        data = self.api.search_runner(runner_name)

        results = data.get("data", {}).get("results", [])
        if not results:
            return None

        df = pd.DataFrame(results)

        # normalize date
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        current_year = datetime.now().year
        df = df[df["date"].dt.year >= current_year - years_back]

        # distance filter
        distance_map = {
            "5K": 5000,
            "10K": 10000,
            "15K": 15000,
            "21K": 21000,
            "42K": 42195
        }

        target = distance_map.get(category)
        if not target:
            return None

        df = df[
            (df["distance"] >= target - 200) &
            (df["distance"] <= target + 200)
        ]

        if df.empty:
            return None

        df["best_time"] = (
            pd.to_numeric(df["personal_time"], errors="coerce")
            .fillna(pd.to_numeric(df["result"], errors="coerce"))
        )

        df = df[df["best_time"].notna()]
        if df.empty:
            return None

        best = df.loc[df["best_time"].idxmin()]

        return {
            "first_name": runner_name.split(" ")[0],
            "last_name": runner_name.split(" ")[1] if " " in runner_name else "",
            "event": best.get("event_name"),
            "race": best.get("race_name"),
            "time": best["best_time"],
            "date": best.get("date"),
        }

        
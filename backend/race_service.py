class RaceService:
    def __init__(self, engine: RaceResultEngine):
        self.engine = engine

    def get_best_results_for_list(self, runners, category, years_back):
        results = []

        for runner in runners:
            res = self.engine.get_best_result(
                runner,
                category,
                years_back
            )
            if res:
                results.append(res)

        df = pd.DataFrame(results)

        if df.empty:
            return df

        df["race_time"] = pd.to_numeric(df["time"])
        df = df.sort_values("race_time")

        return df

        
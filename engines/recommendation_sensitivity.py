from twin.experimental_metrics import (
    ExperimentalMetrics,
)


class RecommendationSensitivityEngine:

    def apply(
        self,
        metrics: list[
            ExperimentalMetrics
        ],
    ) -> None:

        conditions = {
            item.condition
            for item in metrics
        }

        for condition in conditions:

            condition_metrics = [
                item
                for item in metrics
                if item.condition
                == condition
            ]

            baseline = next(
                (
                    item
                    for item
                    in condition_metrics
                    if item.mode
                    == "B0_MACHINE_ONLY"
                ),
                None,
            )

            if (
                baseline is None
                or baseline
                .recommendation_irrigation_mm
                is None
            ):
                continue

            baseline_mm = (
                baseline
                .recommendation_irrigation_mm
            )

            for item in condition_metrics:

                if (
                    item
                    .recommendation_irrigation_mm
                    is None
                ):
                    continue

                current_mm = (
                    item
                    .recommendation_irrigation_mm
                )

                item.recommendation_sensitivity_mm = (
                    abs(
                        current_mm
                        - baseline_mm
                    )
                )

                item.recommendation_changed_from_b0 = (
                    1.0
                    if (
                        current_mm
                        != baseline_mm
                    )
                    else 0.0
                )
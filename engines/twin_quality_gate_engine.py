from twin.trusted_state import (
    TrustedTwinState,
)

from twin.state_confidence import (
    UncertaintyLevel,
)

from twin.quality_gate import (
    TwinQualityGateResult,
    TwinReadinessStatus,
)


class TwinQualityGateEngine:

    def __init__(
        self,
        critical_variables: (
            set[str] | None
        ) = None,
    ):

        self.critical_variables = (
            critical_variables
            if critical_variables is not None
            else {
                "soil_water_state",
            }
        )


    def evaluate(
        self,
        trusted_state: TrustedTwinState,
    ) -> TwinQualityGateResult:

        degraded_variables = []

        missing_current_state_variables = []

        update_required_variables = list(
            trusted_state
            .update_required_variables
        )

        blocking_reasons = []

        warnings = []


        # =================================================
        # 1. EVALUAR VARIABLES CRÍTICAS
        # =================================================

        for variable in (
            self.critical_variables
        ):

            state_variable = (
                trusted_state.get(
                    variable
                )
            )

            # ---------------------------------------------
            # Variable completamente ausente
            # ---------------------------------------------

            if state_variable is None:

                missing_current_state_variables.append(
                    variable
                )

                blocking_reasons.append(
                    (
                        f"Critical variable "
                        f"'{variable}' has no "
                        f"available evidence."
                    )
                )

                continue


            # ---------------------------------------------
            # Existe evidencia pero no estado actual
            # ---------------------------------------------

            if state_variable.value is None:

                missing_current_state_variables.append(
                    variable
                )

                blocking_reasons.append(
                    (
                        f"Critical variable "
                        f"'{variable}' has no "
                        f"trusted current-state value."
                    )
                )


            # ---------------------------------------------
            # Incertidumbre alta
            # ---------------------------------------------

            if (
                state_variable
                .confidence
                .uncertainty_level
                == UncertaintyLevel.HIGH
            ):

                degraded_variables.append(
                    variable
                )

                warnings.append(
                    (
                        f"Critical variable "
                        f"'{variable}' has HIGH "
                        f"uncertainty."
                    )
                )


            # ---------------------------------------------
            # Incertidumbre media
            # ---------------------------------------------

            elif (
                state_variable
                .confidence
                .uncertainty_level
                == UncertaintyLevel.MEDIUM
            ):

                degraded_variables.append(
                    variable
                )

                warnings.append(
                    (
                        f"Critical variable "
                        f"'{variable}' has MEDIUM "
                        f"uncertainty."
                    )
                )


        # =================================================
        # 2. EVIDENCIA EXCLUIDA
        # =================================================

        if (
            trusted_state
            .excluded_evidence_ids
        ):

            warnings.append(
                (
                    f"{len(trusted_state.excluded_evidence_ids)} "
                    f"evidence item(s) were excluded."
                )
            )


        # =================================================
        # 3. DECIDIR ESTADO GLOBAL
        # =================================================

        if blocking_reasons:

            status = (
                TwinReadinessStatus
                .INSUFFICIENT_DATA
            )

            recommendation_allowed = False

        elif degraded_variables:

            status = (
                TwinReadinessStatus
                .DEGRADED
            )

            recommendation_allowed = True

        else:

            status = (
                TwinReadinessStatus
                .READY
            )

            recommendation_allowed = True


        return TwinQualityGateResult(
            status=status,

            recommendation_allowed=(
                recommendation_allowed
            ),

            degraded_variables=(
                sorted(
                    set(
                        degraded_variables
                    )
                )
            ),

            missing_current_state_variables=(
                sorted(
                    set(
                        missing_current_state_variables
                    )
                )
            ),

            update_required_variables=(
                update_required_variables
            ),

            blocking_reasons=(
                blocking_reasons
            ),

            warnings=warnings,

            metadata={
                "critical_variables": (
                    sorted(
                        self.critical_variables
                    )
                ),

                "trusted_variable_count": (
                    len(
                        trusted_state
                        .variables
                    )
                ),
            },
        )
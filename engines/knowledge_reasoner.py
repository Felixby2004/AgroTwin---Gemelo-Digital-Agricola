from twin.farmer_knowledge import (
    FarmerKnowledgeItem,
    FarmerKnowledgeType,
    KnowledgeValidationStatus,
)

from twin.knowledge_effects import (
    KnowledgeEffect,
    KnowledgeEffectType,
)


class KnowledgeReasoner:

    def reason(
        self,
        knowledge: FarmerKnowledgeItem,
    ) -> list[KnowledgeEffect]:

        knowledge.validate()

        if (
            knowledge.validation_status
            == KnowledgeValidationStatus.REJECTED
        ):
            return [
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,
                    effect_type=(
                        KnowledgeEffectType.NO_COMPUTATIONAL_EFFECT
                    ),
                    reason=(
                        "El conocimiento fue rechazado "
                        "y se conserva únicamente para trazabilidad."
                    ),
                )
            ]

        if (
            knowledge.validation_status
            == KnowledgeValidationStatus.EXPIRED
        ):
            return [
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,
                    effect_type=(
                        KnowledgeEffectType.NO_COMPUTATIONAL_EFFECT
                    ),
                    reason=(
                        "El conocimiento ha expirado."
                    ),
                )
            ]

        if (
            knowledge.knowledge_type
            == FarmerKnowledgeType.OBSERVATION
        ):
            return self._observation(
                knowledge
            )

        if (
            knowledge.knowledge_type
            == FarmerKnowledgeType.EVENT
        ):
            return self._event(
                knowledge
            )

        if (
            knowledge.knowledge_type
            == FarmerKnowledgeType.CONSTRAINT
        ):
            return self._constraint(
                knowledge
            )

        if (
            knowledge.knowledge_type
            == FarmerKnowledgeType.PREFERENCE
        ):
            return self._preference(
                knowledge
            )

        if (
            knowledge.knowledge_type
            == FarmerKnowledgeType.LOCAL_KNOWLEDGE
        ):
            return self._local_knowledge(
                knowledge
            )

        return []


    def _observation(
        self,
        knowledge: FarmerKnowledgeItem,
    ) -> list[KnowledgeEffect]:

        effects = [
            KnowledgeEffect(
                knowledge_id=knowledge.knowledge_id,

                effect_type=(
                    KnowledgeEffectType.ADD_CONTEXT
                ),

                target=(
                    knowledge.affects[0]
                    if knowledge.affects
                    else None
                ),

                parameters={
                    "payload": knowledge.payload,
                    "spatial_scope":
                        knowledge.spatial_scope,
                },

                reason=(
                    "La observación humana aporta "
                    "evidencia contextual sin sobrescribir "
                    "el estado medido."
                ),
            )
        ]

        if (
            knowledge.validation_status
            == KnowledgeValidationStatus.UNVERIFIED
        ):
            effects.append(
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,

                    effect_type=(
                        KnowledgeEffectType.REQUEST_VALIDATION
                    ),

                    reason=(
                        "La observación humana aún "
                        "no ha sido validada."
                    ),
                )
            )

        return effects


    def _event(
        self,
        knowledge: FarmerKnowledgeItem,
    ) -> list[KnowledgeEffect]:

        if (
            knowledge.validation_status
            != KnowledgeValidationStatus.CONFIRMED
        ):
            return [
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,

                    effect_type=(
                        KnowledgeEffectType.REQUEST_VALIDATION
                    ),

                    reason=(
                        "Un evento humano no puede modificar "
                        "el historial físico hasta ser confirmado."
                    ),
                )
            ]

        return [
            KnowledgeEffect(
                knowledge_id=knowledge.knowledge_id,

                effect_type=(
                    KnowledgeEffectType.ADD_CONFIRMED_EVENT
                ),

                target="event_history",

                parameters={
                    "event": knowledge.payload,
                },

                reason=(
                    "Evento humano confirmado."
                ),
            ),

            KnowledgeEffect(
                knowledge_id=knowledge.knowledge_id,

                effect_type=(
                    KnowledgeEffectType.RECOMPUTE_STATE
                ),

                target="biophysical_state",

                reason=(
                    "El evento confirmado puede cambiar "
                    "el estado biofísico derivado."
                ),
            ),
        ]


    def _constraint(
        self,
        knowledge: FarmerKnowledgeItem,
    ) -> list[KnowledgeEffect]:

        if (
            knowledge.validation_status
            != KnowledgeValidationStatus.CONFIRMED
        ):
            return [
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,

                    effect_type=(
                        KnowledgeEffectType.REQUEST_VALIDATION
                    ),

                    reason=(
                        "Una restricción debe confirmarse "
                        "antes de limitar acciones."
                    ),
                )
            ]

        return [
            KnowledgeEffect(
                knowledge_id=knowledge.knowledge_id,

                effect_type=(
                    KnowledgeEffectType.FILTER_ACTIONS
                ),

                target="candidate_actions",

                parameters={
                    "constraint":
                        knowledge.payload,

                    "constraint_type": (
                        knowledge.constraint_type.value
                        if knowledge.constraint_type
                        else None
                    ),
                },

                reason=(
                    "La restricción confirmada limita "
                    "el conjunto de acciones factibles."
                ),
            )
        ]


    def _preference(
        self,
        knowledge: FarmerKnowledgeItem,
    ) -> list[KnowledgeEffect]:

        if (
            knowledge.validation_status
            != KnowledgeValidationStatus.CONFIRMED
        ):
            return [
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,

                    effect_type=(
                        KnowledgeEffectType.REQUEST_VALIDATION
                    ),

                    reason=(
                        "La preferencia debe estar activa "
                        "y confirmada para modificar el ranking."
                    ),
                )
            ]

        return [
            KnowledgeEffect(
                knowledge_id=knowledge.knowledge_id,

                effect_type=(
                    KnowledgeEffectType.MODIFY_RANKING
                ),

                target="scenario_ranking",

                parameters={
                    "preference":
                        knowledge.payload,
                },

                reason=(
                    "La preferencia modifica el ranking, "
                    "no el estado biofísico."
                ),
            )
        ]


    def _local_knowledge(
        self,
        knowledge: FarmerKnowledgeItem,
    ) -> list[KnowledgeEffect]:

        effects = [
            KnowledgeEffect(
                knowledge_id=knowledge.knowledge_id,

                effect_type=(
                    KnowledgeEffectType.BRANCH_SCENARIO
                ),

                target=(
                    knowledge.affects[0]
                    if knowledge.affects
                    else None
                ),

                parameters={
                    "hypothesis":
                        knowledge.payload,

                    "spatial_scope":
                        knowledge.spatial_scope,
                },

                reason=(
                    "El conocimiento local crea una "
                    "hipótesis alternativa sin modificar "
                    "los parámetros originales."
                ),
            )
        ]

        if (
            knowledge.validation_status
            == KnowledgeValidationStatus.UNVERIFIED
        ):
            effects.append(
                KnowledgeEffect(
                    knowledge_id=knowledge.knowledge_id,

                    effect_type=(
                        KnowledgeEffectType.REQUEST_VALIDATION
                    ),

                    reason=(
                        "La hipótesis local todavía "
                        "no ha sido validada."
                    ),
                )
            )

        return effects
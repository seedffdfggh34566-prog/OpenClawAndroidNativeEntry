from __future__ import annotations

from collections import defaultdict

from backend.sales_workspace.schemas import (
    CandidateRankingBoard,
    CandidateRankingItem,
    RankingDelta,
    SalesWorkspace,
    utc_now,
)


SIGNAL_WEIGHTS = {
    "fit": 20,
    "pain": 20,
    "timing": 15,
    "region": 10,
    "source_quality": 10,
    "other": 3,
}

SOURCE_RELIABILITY_BONUS = {
    "high": 10,
    "medium": 5,
    "low": 1,
}


def derive_candidate_ranking(workspace: SalesWorkspace) -> CandidateRankingBoard:
    previous_items = {}
    if workspace.ranking_board:
        previous_items = {
            item.candidate_id: item
            for item in workspace.ranking_board.ranked_items
        }

    observations_by_candidate = defaultdict(list)
    for observation in workspace.candidate_observations.values():
        observations_by_candidate[observation.candidate_id].append(observation)

    scored_items: list[tuple[str, int, dict[str, int], list[str], str]] = []
    for candidate_id, candidate in workspace.company_candidates.items():
        if candidate.status == "archived":
            continue

        score = 0
        breakdown: dict[str, int] = defaultdict(int)
        supporting_observation_ids: list[str] = []
        positive_signals: set[str] = set()

        for observation in observations_by_candidate.get(candidate_id, []):
            source = workspace.research_sources.get(observation.source_id)
            reliability_bonus = SOURCE_RELIABILITY_BONUS.get(source.reliability, 0) if source else 0

            if observation.signal_type == "exclusion" or observation.polarity == "negative":
                signal_score = -100 * observation.strength
            else:
                base_weight = SIGNAL_WEIGHTS.get(observation.signal_type, SIGNAL_WEIGHTS["other"])
                signal_score = (base_weight * observation.strength) + reliability_bonus
                positive_signals.add(observation.signal_type)
                supporting_observation_ids.append(observation.id)

            breakdown[observation.signal_type] += signal_score
            score += signal_score

        if not supporting_observation_ids:
            reason = "No evidence-backed positive observations yet"
        else:
            reason = " + ".join(sorted(positive_signals)) + " evidence"

        scored_items.append((candidate_id, score, dict(breakdown), supporting_observation_ids, reason))

    scored_items.sort(key=lambda item: (-item[1], item[0]))

    ranked_items: list[CandidateRankingItem] = []
    for rank, (candidate_id, score, breakdown, supporting_ids, reason) in enumerate(scored_items, start=1):
        candidate = workspace.company_candidates[candidate_id]
        ranked_items.append(
            CandidateRankingItem(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                rank=rank,
                score=score,
                status=candidate.status,
                reason=reason,
                supporting_observation_ids=supporting_ids,
                score_breakdown=breakdown,
            )
        )

    deltas: list[RankingDelta] = []
    for item in ranked_items:
        previous = previous_items.get(item.candidate_id)
        if previous is None:
            reason = f"{item.candidate_name} entered ranking at #{item.rank} with {item.reason}."
            previous_rank = None
            previous_score = 0
        elif previous.rank != item.rank or previous.score != item.score:
            reason = (
                f"{item.candidate_name} moved from #{previous.rank} to #{item.rank}; "
                f"score changed from {previous.score} to {item.score} based on {item.reason}."
            )
            previous_rank = previous.rank
            previous_score = previous.score
        else:
            continue

        deltas.append(
            RankingDelta(
                candidate_id=item.candidate_id,
                previous_rank=previous_rank,
                new_rank=item.rank,
                previous_score=previous_score,
                new_score=item.score,
                reason=reason,
                supporting_observation_ids=item.supporting_observation_ids,
            )
        )

    return CandidateRankingBoard(
        id=f"board_v{workspace.workspace_version}",
        workspace_id=workspace.id,
        workspace_version=workspace.workspace_version,
        ranked_items=ranked_items,
        deltas=deltas,
        generated_at=utc_now(),
    )

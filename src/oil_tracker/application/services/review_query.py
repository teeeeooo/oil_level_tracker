from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from statistics import median

from oil_tracker.domain.review import (
    LowConfidenceInterval,
    ReviewBundle,
    ReviewCategory,
    ReviewEvent,
    ReviewFilter,
    ReviewOverlayData,
    ReviewTrackingSample,
)


_EXPLICIT_REVIEW_FLAGS = {
    "LOW_CONFIDENCE",
    "DETECTION_LOST",
    "FOGGED_OR_GLARE",
    "REVIEW_REQUIRED",
    "UNKNOWN_REVIEW",
}


class ReviewQueryModel:
    """Qt-independent time query and review-item index for one result bundle."""

    def __init__(self, bundle: ReviewBundle) -> None:
        self.bundle = bundle
        grouped_samples: dict[str, list[ReviewTrackingSample]] = defaultdict(list)
        grouped_events: dict[str, list[ReviewEvent]] = defaultdict(list)
        for sample in bundle.samples:
            grouped_samples[sample.glass_id].append(sample)
        for event in bundle.events:
            grouped_events[event.glass_id].append(event)
        self._samples = {
            glass_id: tuple(sorted(values, key=lambda item: (item.timestamp_sec, item.frame_index, item.input_order)))
            for glass_id, values in grouped_samples.items()
        }
        self._sample_times = {
            glass_id: tuple(item.timestamp_sec for item in values)
            for glass_id, values in self._samples.items()
        }
        self._events = {
            glass_id: tuple(
                sorted(
                    values,
                    key=lambda item: (
                        item.start_time_sec,
                        item.end_time_sec if item.end_time_sec is not None else item.start_time_sec,
                        item.event_type.value,
                        item.input_order,
                    ),
                )
            )
            for glass_id, values in grouped_events.items()
        }
        self._intervals = {
            glass.id: self._build_low_confidence_intervals(glass.id)
            for glass in bundle.glasses
        }

    def samples_for_glass(self, glass_id: str) -> tuple[ReviewTrackingSample, ...]:
        return self._samples.get(glass_id, ())

    def events_for_glass(self, glass_id: str) -> tuple[ReviewEvent, ...]:
        return self._events.get(glass_id, ())

    def low_confidence_intervals(self, glass_id: str) -> tuple[LowConfidenceInterval, ...]:
        return self._intervals.get(glass_id, ())

    def filtered_intervals(
        self,
        glass_id: str,
        review_filter: ReviewFilter = ReviewFilter.ALL,
    ) -> tuple[LowConfidenceInterval, ...]:
        return tuple(
            interval
            for interval in self.low_confidence_intervals(glass_id)
            if interval.matches(review_filter)
        )

    def sample_at(self, glass_id: str, timestamp_sec: float) -> ReviewTrackingSample | None:
        if not self.within_analysis_range(timestamp_sec):
            return None
        samples = self._samples.get(glass_id, ())
        if not samples:
            return None
        index = bisect_right(self._sample_times[glass_id], float(timestamp_sec)) - 1
        return samples[index] if index >= 0 else None

    def within_analysis_range(self, timestamp_sec: float) -> bool:
        return self.bundle.analysis_start_sec <= timestamp_sec <= self.bundle.analysis_end_sec

    def overlay_at(self, glass_id: str, timestamp_sec: float) -> ReviewOverlayData:
        within = self.within_analysis_range(timestamp_sec)
        sample = self.sample_at(glass_id, timestamp_sec) if within else None
        glass = self.bundle.glass_config(glass_id)
        zero_line_y = glass.geometry.zero_line_y if glass is not None else None
        oil_y = sample.oil_boundary_y(zero_line_y) if sample is not None else None
        foam_y = sample.foam_front_y(zero_line_y) if sample is not None else None
        reasons = (
            review_reasons(sample, glass.detector_settings.minimum_final_confidence)
            if sample is not None and glass is not None
            else ()
        )
        boundary_status = ""
        if glass is not None:
            outside = []
            if oil_y is not None and glass.geometry.ellipse.horizontal_extent_at(oil_y) is None:
                oil_y = None
                outside.append("유면 위치가 관찰창 타원 밖에 있어 표시하지 않음")
            if foam_y is not None and glass.geometry.ellipse.horizontal_extent_at(foam_y) is None:
                foam_y = None
                outside.append("거품 경계가 관찰창 타원 밖에 있어 표시하지 않음")
            boundary_status = "; ".join(outside)
        return ReviewOverlayData(
            glass_id=glass_id,
            video_timestamp_sec=float(timestamp_sec),
            sample=sample,
            oil_boundary_y=oil_y,
            foam_front_y=foam_y,
            within_analysis_range=within,
            review_reasons=reasons,
            boundary_status=boundary_status,
        )

    def previous_event(self, glass_id: str, timestamp_sec: float) -> ReviewEvent | None:
        candidates = [event for event in self.events_for_glass(glass_id) if event.start_time_sec < timestamp_sec]
        return candidates[-1] if candidates else None

    def next_event(self, glass_id: str, timestamp_sec: float) -> ReviewEvent | None:
        return next((event for event in self.events_for_glass(glass_id) if event.start_time_sec > timestamp_sec), None)

    def previous_review(
        self,
        glass_id: str,
        timestamp_sec: float,
        review_filter: ReviewFilter,
    ) -> LowConfidenceInterval | None:
        candidates = [
            interval
            for interval in self.filtered_intervals(glass_id, review_filter)
            if interval.representative_time_sec < timestamp_sec
        ]
        return candidates[-1] if candidates else None

    def next_review(
        self,
        glass_id: str,
        timestamp_sec: float,
        review_filter: ReviewFilter,
    ) -> LowConfidenceInterval | None:
        return next(
            (
                interval
                for interval in self.filtered_intervals(glass_id, review_filter)
                if interval.representative_time_sec > timestamp_sec
            ),
            None,
        )

    def active_events(self, glass_id: str, timestamp_sec: float) -> tuple[ReviewEvent, ...]:
        tolerance = self.nominal_interval(glass_id) / 2.0
        active = []
        for event in self.events_for_glass(glass_id):
            if event.end_time_sec is not None:
                if event.start_time_sec <= timestamp_sec <= event.end_time_sec:
                    active.append(event)
            elif abs(event.start_time_sec - timestamp_sec) <= tolerance:
                active.append(event)
        return tuple(active)

    def nominal_interval(self, glass_id: str) -> float:
        if self.bundle.session.sampling_fps > 0:
            return 1.0 / self.bundle.session.sampling_fps
        values = self.samples_for_glass(glass_id)
        deltas = [
            right.timestamp_sec - left.timestamp_sec
            for left, right in zip(values, values[1:])
            if right.timestamp_sec > left.timestamp_sec
        ]
        return median(deltas) if deltas else 0.5

    def _build_low_confidence_intervals(self, glass_id: str) -> tuple[LowConfidenceInterval, ...]:
        glass = self.bundle.glass_config(glass_id)
        if glass is None:
            return ()
        threshold = glass.detector_settings.minimum_final_confidence
        flagged = [
            (
                sample,
                review_reasons(sample, threshold),
                review_categories(sample, threshold),
            )
            for sample in self.samples_for_glass(glass_id)
            if self.bundle.analysis_start_sec <= sample.timestamp_sec <= self.bundle.analysis_end_sec
        ]
        flagged = [item for item in flagged if item[1] or item[2]]
        if not flagged:
            return ()
        nominal = self.nominal_interval(glass_id)
        maximum_gap = max(nominal * 1.75, 1e-6)
        groups = [[flagged[0]]]
        for current in flagged[1:]:
            if current[0].timestamp_sec - groups[-1][-1][0].timestamp_sec <= maximum_gap:
                groups[-1].append(current)
            else:
                groups.append([current])
        intervals = []
        for group in groups:
            representative = min(
                group,
                key=lambda item: (
                    item[0].overall_confidence,
                    item[0].timestamp_sec,
                    item[0].frame_index,
                    item[0].input_order,
                ),
            )[0]
            reasons = tuple(sorted({reason for _sample, sample_reasons, _categories in group for reason in sample_reasons}))
            categories = tuple(
                sorted(
                    {category for _sample, _reasons, sample_categories in group for category in sample_categories},
                    key=lambda item: item.value,
                )
            )
            intervals.append(
                LowConfidenceInterval(
                    glass_id=glass_id,
                    start_time_sec=group[0][0].timestamp_sec,
                    end_time_sec=group[-1][0].timestamp_sec,
                    representative_time_sec=representative.timestamp_sec,
                    minimum_confidence=min(sample.overall_confidence for sample, _reasons, _categories in group),
                    reasons=reasons,
                    sample_count=len(group),
                    categories=categories,
                )
            )
        return tuple(intervals)


def review_categories(sample: ReviewTrackingSample, minimum_confidence: float) -> tuple[ReviewCategory, ...]:
    categories: set[ReviewCategory] = set()
    if not sample.is_valid:
        categories.add(ReviewCategory.INVALID)
    if sample.overall_confidence < minimum_confidence:
        categories.add(ReviewCategory.LOW_CONFIDENCE)
    flags = {flag.strip().upper() for flag in sample.flags if flag.strip()}
    for flag in flags:
        if "LOW_CONFIDENCE" in flag:
            categories.add(ReviewCategory.LOW_CONFIDENCE)
        if "REVIEW" in flag or "UNKNOWN_REVIEW" in flag:
            categories.add(ReviewCategory.REVIEW_REQUIRED)
        if "FOAM" in flag:
            categories.add(ReviewCategory.FOAM)
        if "GLARE" in flag or "FOG" in flag:
            categories.add(ReviewCategory.GLARE_OR_FOG)
        if "LOST" in flag:
            categories.add(ReviewCategory.DETECTION_LOST)
    return tuple(sorted(categories, key=lambda item: item.value))


def review_reasons(sample: ReviewTrackingSample, minimum_confidence: float) -> tuple[str, ...]:
    reasons: list[str] = []
    if not sample.is_valid:
        reasons.append("유효하지 않은 검출")
    if sample.overall_confidence < minimum_confidence:
        reasons.append("신뢰도 기준 미달")
    normalized_flags = {flag.strip().upper() for flag in sample.flags if flag.strip()}
    for flag in sorted(normalized_flags):
        if flag in _EXPLICIT_REVIEW_FLAGS or "REVIEW" in flag or "FOAM" in flag or "GLARE" in flag or "FOG" in flag or "LOST" in flag:
            reasons.append(flag)
    return tuple(dict.fromkeys(reasons))

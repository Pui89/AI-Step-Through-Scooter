# PUI89 AI Step-Through Scooter — 360° Intelligence Profile v1.0

**Status:** Proposed rider-awareness requirements; no functioning scooter, sensor installation, rider trial or road validation is established.

## Mission
Provide the rider with low-distraction advisory awareness of relevant traffic, road users and hazards around a two-wheel step-through scooter.

## Candidate workflow
1. Define rider position, mounting points, lean/vibration envelope, operating speeds and warning priorities.
2. Evaluate forward, rearward and side/corner sensing with realistic bodywork and rider occlusion.
3. Detect relevant vehicles, pedestrians, animals, obstacles and road-surface context; track only when continuity and timing are reliable.
4. Fuse approved modalities only after calibration and timestamp/frame compatibility checks.
5. Present prioritised, concise warnings without requiring the rider to look at or interact with a screen while moving.

## Candidate AI and sensing
Compact rugged RGB cameras, object detection, segmentation, tracking, optional radar/IMU and read-only vehicle-health data where supported. Any modality must be assessed for vibration, weather, mounting, power, thermal load and rider privacy.

## 360° requirements
- Define rider-centred horizontal/elevation sectors, including rear, side and near-field blind zones.
- Account for rider body, helmet, luggage, lean angle, steering movement, vibration, rain, glare and low-light conditions.
- Do not imply that a panoramic camera eliminates blind spots or provides reliable distance/depth without validation.
- Warnings must be prioritised and tested for comprehension and distraction risk.
- Degraded sensing must be reported; unknown areas must never be shown as clear.

## Safety and exclusions
The rider retains full control. AI must not command steering, throttle or braking. No autonomous riding, collision-prevention guarantee, flood-crossing capability or roadworthiness certification is claimed.

## Evidence gates
Rider hazard analysis → coverage/placement review → synthetic and simulator tests → sensor bench/vibration/weather tests → closed-course evaluation with trained participants → controlled road validation and independent review.

Measure sector coverage, hazard recall/false warnings, time-to-warning, track continuity, latency, vibration/weather robustness, energy, rider comprehension and distraction.

**Shared architecture:** [PUI89 360° Intelligence Architecture v1.0](https://github.com/Pui89/PUI89-Shared-AI-Core/blob/main/docs/PUI89_360_DEGREE_INTELLIGENCE_V1.0.md)

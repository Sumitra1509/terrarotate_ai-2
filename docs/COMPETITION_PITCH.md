# TerraRotate AI · Competition Pitch

## One-liner
From NASA's view of the sky to the farmer's view of their field: evidence-backed crop-rotation exploration for uncertain water and climate conditions.

## The user
A smallholder farmer in Vellore, Tamil Nadu, may know when their field floods or runs out of irrigation, but not have access to usable long-term climate evidence, crop trade-off comparisons, or a simple resilience report.

## Problem
Crop rotation under variable monsoon conditions is a multi-constraint decision. Climate dashboards show data; farmers need locally interpretable alternatives and clear uncertainty.

## Solution
1. The farmer selects the farm, current crop sequence, irrigation, soil, waterlogging, market access and priority.
2. TerraRotate retrieves actual historical NASA POWER estimates and reports rainfall variability, high-heat exposure and dry-spell patterns.
3. A transparent rotation-screening engine compares the baseline with alternatives and surfaces conflicts for local review.
4. Farmers stress-test hypothetical rain/temperature changes and export a report explaining alternatives, evidence and uncertainties.

## Reference design principle
Inspired by Astro Sweepers' decision-support framing: **detect/explain risk → compare practical mitigations → generate decision-ready report**. This project is original and focuses on the 2026 crop-rotation challenge.

## Working demonstration script (2 minutes)
1. Select Vellore and a rice-based rotation.
2. Change irrigation to rainfed and flag waterlogging; point out visible constraints.
3. Fetch a completed historical NASA POWER period; show actual precipitation and hot-day indicators.
4. Move rainfall slider to -20%; compare existing rotation and alternatives, explicitly labeling scores illustrative.
5. Open report tab and download a readable HTML report with provenance and disclaimers.

## Do not overclaim
This early build does not calculate crop water savings, scientific rotation impact, real-time hazard warnings, aquifer depth, or future crop yields. It establishes the testable workflow; scientific integration and agronomic validation remain future work.

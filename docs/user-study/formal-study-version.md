# NextTrack Formal Study Version

## Application Version

Git tag: `evaluation-study-v1`

Git commit:
`a36071549c6e69cb60119c7b8211c0671c3749cd`

Branch:
`feature/evaluation-interface`

## Deployment

Participant interface:

https://nexttrack-vi1q.onrender.com/evaluation

## Study Configuration

Study contexts:

- Rock
- Hip-Hop
- Country

Each comparison contains:

- three fixed recent listening tracks;
- Recommendation Set A containing five tracks;
- Recommendation Set B containing five tracks.

The experimental conditions use exploration levels 0.00 and 1.00.

The conditions are presented as Set A and Set B and are counterbalanced
using participant-code parity. The exploration values are not shown to
participants.

No genre or artist preferences are applied during Study Mode.

## Pilot Revision

Following the pilot evaluation, the participant instructions were
revised to ask participants to briefly listen to at least three
recommendations from Set A and three recommendations from Set B before
rating the sets.

The recommendation algorithm and its parameters were not modified as a
result of the pilot.

## Validation

Before formal evaluation:

- the automated test suite passed;
- the frozen Phase 4 reference verification passed 30/30;
- the deployed Study Mode was smoke-tested;
- Rock, Hip-Hop and Country contexts were verified;
- odd/even participant-code counterbalancing was verified;
- Spotify listening links were verified;
- the post-pilot instruction revision was verified.

## Deployment Freeze

Render automatic deployment was disabled after the formal-study version
was verified.

The deployed application will remain unchanged during formal participant
data collection unless a study-blocking technical defect is identified.

Any such change will be documented and released under a new version
rather than modifying `evaluation-study-v1`.
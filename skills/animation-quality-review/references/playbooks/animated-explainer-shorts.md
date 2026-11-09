# Animated explainer shorts playbook

The style: simple ball-headed characters in rich, moving worlds, telling a surprising story or fact in under about a minute.

**Evidence:** six animated shorts from one public channel, checked in November 2026. That's a small sample from a single creator, so these rules describe this style. They don't prove what works in general.

| Short | Views | Length | % frames near still | Longest hold | Fast moves | Settled after | Words/min | LUFS | Loudness range |
|---|---|---|---|---|---|---|---|---|---|
| The Ancient Jar That Warned an Empire | 32.0M | 65s | 2.0 | 0.23s | 9 | 8/9 | 217 | -14.0 | 2.3 |
| Why Perfect Railroads Don't Work | 23.3M | 65s | 0.6 | 0.17s | 17 | 10/17 | 199 | -14.0 | 3.0 |
| The Job Nobody Wants in Japan | 16.8M | 61s | 0.3 | 0.10s | 7 | 5/7 | 222 | -14.0 | 1.8 |
| Your Brain's Secret Idea Zone | 14.4M | 39s | 1.2 | 0.17s | 1 | 1/1 | 223 | -15.6 | 3.2 |
| Levels of Pirate Cannonballs | 9.0M | 64s | 1.9 | 0.33s | 18 | 11/18 | 206 | -14.0 | 2.1 |
| This Knight Found the Ultimate Loophole | 1.6M | 41s | 0.6 | 0.10s | 6 | 6/6 | 233 | -14.9 | 2.6 |

A seventh short from the channel, "Any Last Words?", was excluded as out of format: it's another creator's comic over game footage.

All six are 1080×1920 at 30fps.

## Detail numbers and targets

Saved in `references/profiles/animated-explainer-shorts.json`, so `measure --against animated-explainer-shorts` scores a new video against them automatically.

| Short | Fine detail (edge %) | Colours per frame | Contrast | Saturation | Median motion |
|---|---|---|---|---|---|
| Ancient Jar | 4.31 | 538 | 150 | 40.8 | 8.22 |
| Railroads | 4.36 | 688 | 154 | 47.3 | 11.32 |
| Japan | 3.68 | 559 | 169 | 40.1 | 8.86 |
| Idea Zone | 3.31 | 276 | 164 | 48.5 | 4.22 |
| Pirate | 3.49 | 573 | 155 | 48.4 | 10.71 |
| Knight | 4.71 | 786 | 166 | 48.3 | 9.78 |

| Measure | References | Target |
|---|---|---|
| Fine detail (edge %) | 3.31 to 4.71 | 4.0+ |
| Colours per frame | 276 to 786 | 550+ |
| Contrast | 150 to 169 | 150 to 169 |
| Saturation | 40.1 to 48.5 | 40 to 48.5 |
| Median motion | 4.22 to 11.32 | 6+ |
| Near-still frames | 0.3% to 2% | 2% or less |
| Longest hold | 0.1s to 0.33s | 0.33s or less |
| Fast camera moves | 1 to 18 | 18 or less |
| Cut candidates, before checking by eye | 0 to 5 | 8 or less |
| Words per minute | 199 to 233 | 199 to 233 |
| Loudness | -15.6 to -14 LUFS | -15.6 to -13.5 LUFS |
| Loudness range | 1.8 to 3.2 LU | 1.8 to 3.2 LU |
| True peak | -2.9 to -1.6 dB | -1 dB or less |
| Silent gaps over 0.15s | 0 | None |

**Where the targets come from.** The ranges are measured. The targets were chosen in November 2026 while polishing one short, aiming at the richer videos here. They aren't rules: only Railroads and Knight meet both the detail and colour targets. Idea Zone misses three and reached 14.4M, so treat a miss that's within the references as a choice.

**How much these can be trusted.** On the same film, 4K, 1080p and a 5 Mbps upload-style copy scored within 4% on colours and matched on detail, contrast and saturation, so a master can fairly be compared with downloaded references. All six references score nothing outside the range, which is true by construction, so that isn't proof of accuracy. A weak early cut of one short fell outside on 5 measures, and its polished version on 3.

**Targets video numbers can't check.** Check these from the project's shot list or by eye:

- Real body pose changes on at least 60% of frames that have a character on screen, not counting breathing and sway
- At least 3 expressions for each supporting character
- At least 3 kinds of scene change, with whips under half of them

## Core rules: in all six

1. **The camera never rests.** Measured: at most 2% of frames are near still, and no hold lasts longer than 0.33s. Even calm shots drift.
2. **The picture shows the words being said right now.** Seen: "a coin" puts a coin in the rail gap, "no work" shows an empty desk with outlines where things used to be, "hull" shows the ball hitting the hull. This is what makes the pace followable at over 200 words a minute.
3. **Characters are the simplest thing on screen.** Seen: all share a white ball head, a capsule body, stick limbs and a face of a few lines, with a thick outline. Everything around them has more detail. Character design barely changes between stories.
4. **Identity comes from a hat and a colour.** Seen: flat cap vs bowler vs top hat, and bandana colours on the pirates. You can tell people apart at phone size without reading a face.
5. **Scene changes are hidden.** Stepping through every detector candidate confirmed only 2 hard cuts across all six (Jar 3.07s, Pirate 2.2s). The rest are hidden with one of:
   - a dissolve, usually mid-move, from 1–3 frames (Knight 29.7s) to about 8 frames (Jar 7.4s)
   - a camera flight through the space (Railroads 9.2s)
   - something in the world filling the screen, such as cannon smoke (Pirate 18.0s, 59.8s)
6. **Light and colour change with the story.** Seen: the same jar is relit grey, sunset-toned and blue. The pirate ship goes from day to purple sunset. The office goes from white to blue gloom. Sometimes colour is the information: the railroad's rails shift through purple, pink and yellow as they heat up.
7. **Captions are plain and fixed.** Seen: 1–3 words, white heavy type with a black outline, at about 70% of the frame height, changing with the words. They don't compete with the picture.
8. **Audio is dense and steady.** Measured: 199–233 words a minute, -14 to -15.6 LUFS, a loudness range of 1.8–3.2 LU, and no gaps over 0.15s below -35 dB. Voice quality and sound design weren't assessed, because these numbers can't judge them.
9. **The first line is a strange claim.** Read from transcripts: "A knight paid a priest to forgive a crime he hadn't committed yet." "If you fall asleep holding two steel balls, you might wake up a genius."

## Common rules: in most, with exceptions

10. **"You see," turns from hook to explanation.** In 5 of 6, not Pirate. In Japan it comes late, as the reveal.
11. **Key terms appear as signs in the world.** In 5 of 6, not Jar: a barrel labelled LANGRAGE, a door marked CAREER DEVELOPMENT ROOM, the pardon document. They're usually consistent and legible from several angles.
12. **Fast moves cluster early.** At least half are in the first third in 4 of 6 (Jar 8/9, Pirate 14/18, Knight 4/6, Japan 4/7). Railroads spreads them out, and Idea Zone has only one.
13. **Fast moves settle.** Motion dropped below half its peak after 41 of 58 fast moves. It's clearest in Jar (8/9) and Knight (6/6), and looser in Railroads and Pirate, which often move straight into the next action.
14. **The tall frame gets stacked.** Seen by eye in all six, not measured: dragon over frog, bulb over plates, a tower of sin prices. Foreground objects often sit large in front of the action.
15. **Expressions switch fast.** Seen in all six. The timing was stepped through in only two: Jar (laughing to deadpan in about 0.4s, and the emperor's face flips to laughing right on the word "burst" at about 6.0s) and Railroads (smug to wide grin in about 0.5s).

## Varies: a choice, not a rule

- **How rich the world is.** Jar and Railroads look strongly 3D, with texture and reflections. Japan is clean, flat-shaded linework. Idea Zone is one dim room with diagrams. All of them work, so don't assume you need heavy rendering.
- **How many fast moves.** From 1 to 18. Idea Zone reached 14.4M with one, so slow and steady is viable.
- **The size of the payoff.** Jar, Railroads and Pirate end big and physical. Japan, Idea Zone and Knight end on something small and clear: a door, a notepad, a piece of paper.
- **Story or facts.** Some are stories with a mocked hero and a reversal. Pirate is a list that escalates. Idea Zone is an explanation.

## Unknown

- **What drives views.** Knight has the same style as Jar and was uploaded a day apart, at a twentieth of the views, so the style doesn't explain reach by itself. Topic and story probably matter a lot, but this sample can't separate them. Other videos differ in age: Railroads reached 23M in about 5 days.
- **How they're made.** Inferred only: signs and room layouts stay consistent as the camera orbits, which suggests real 3D scenes with flat characters placed inside. A few melted-looking objects, such as the statue at Jar 14.5s, might be generated models. Nothing confirms either.
- **Voice, music and sound.** Not heard.

## Review checklist

**Judge from a script or storyboard:**

- [ ] The first line is a strange, specific claim, not a topic (rule 9)
- [ ] Every key word has a planned image (rule 2)
- [ ] Characters are identifiable by hat and colour alone (rules 3, 4)
- [ ] There's a colour plan by story beat, and the same sets get relit (rule 6)
- [ ] Every scene change has a planned way to hide it (rule 5)
- [ ] Words per minute around 200–230: count words against target length (rule 8)

**Judge from a cut, using `measure` and the frames:**

- [ ] Run `measure --against animated-explainer-shorts` and read `scorecard.md`
- [ ] Under about 2% of frames near still, with no hold over about 0.33s (rule 1)
- [ ] Hard cuts are rare once candidates have been checked by eye (rule 5)
- [ ] Captions are 1–3 words, fixed in place, clear of faces and platform buttons (rule 7)
- [ ] About -14 LUFS with a narrow loudness range and no dead air (rule 8)
- [ ] Listen to it yourself, because these checks can't assess the voice and sound

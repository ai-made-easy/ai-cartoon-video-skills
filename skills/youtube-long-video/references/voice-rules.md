# Voice rules for a long video

A short video and a long video need different voices. A short runs at 200 words a minute or more with no gaps. A long video at that speed is tiring after two minutes. The numbers below come from the reference video's own voice (measured from its audio) and from what fixed our first attempt. They are targets to aim at, not a script: this skill ships no voice tools.

## Pace

- Around 130 words a minute (range 120 to 140). The reference measured 129. Our first video was at 173 and felt rushed.
- Count it: words in the narration divided by minutes of the voice track. If you are over 145, the voice is too fast or the pauses are missing.
- A 15 minute video is about 2,000 words, not 3,000.

## Pitch

- Pitch should move inside a range. The reference had a range of about 12.5 semitones (low to high of the whole voice) and an average movement of 4.2 semitones between neighbouring points. Our first video was at 9.4 and 2.7: flat.
- A flat read is the main failure. Theatrical is the other one: do not push the range up to make it exciting.
- Questions rise at the end (up to about 3 semitones over the last half second).
- One key word every one or two sentences gets a little lift (about 1.5 semitones and 2 dB louder). Mark them in the script with asterisks, for example `He walked in, *protected* their temples.`, strip the asterisks before the voice reads them, and never show them on screen. Mark contrast and reveal words (not, never, only, first, still), the number that makes a fact surprising, a name at its big moment. Never mark "the", "a" or "of".

How we got there (one recipe that worked, not the only one): slow each sentence to 0.87 times speed with pitch kept, widen the pitch movement by a factor of 1.4 around each sentence's median pitch, add the question rise and the emphasis lift, then put the sentences together with real pauses. A tool such as Praat (through the parselmouth Python package) does the pitch work. The result was about 15 percent longer and moved from 173 to about 148 words a minute, and from 11.9 to 15.6 semitones of range on the opening.

## Pauses

- Real silences between sentences: about 0.4 seconds.
- A longer one, about 0.55 seconds extra, before a sentence that starts with "But", "Yet", "Still" or "And yet".
- About 0.35 seconds extra before a question that follows a statement.
- A paragraph break gets at least as long as a sentence gap.
- While a story scene plays its dialogue, the narrator stops; the narrator comes back for the punchline.

## Spelling and pronunciation

- Plain spelling for common words. Never respell a common English word to "help" the voice (do not write "bab-ih-lon" for Babylon). Inventing stress respellings made a good voice mispronounce ordinary words in our first video.
- No dashes inside a word. A respelling with hyphens makes the voice read each piece separately and it sounds choppy. If a rare name is said wrongly, change it once to one continuous word, then listen again.
- Test a doubtful word first in a tiny throwaway line, not in the whole video.
- A number at the very end of a sentence can be swallowed ("fifteen miles."). Put one more word after it ("fifteen miles away.").
- Check every clip by speech-to-text: transcribe the recording and compare it with the script. A missing word, a clipped first or last word, or a word heard as something else is a failure; record that sentence again. A check that skips respelled words hides exactly the words that go wrong.

## Words on the page (the script)

- Say each idea once. The hook, the middle and the recap must not explain the same thing in other words.
- A hook in the first seconds, the story starts within the first minute.
- Fewer events, each told as a small story (set-up, what people said or did, a twist or punchline), beat many events in one line each. About one story-worthy moment per minute, with a line or two on the map in between.
- Write like a person explaining to a friend, not like a slide.
- Quotes: put the exact words in quotation marks only if you copied them character for character from the source; otherwise paraphrase and do not use quotation marks.

## Loudness

Level the final mix to a normal streaming level (around -14 LUFS integrated, true peak no higher than -1.5 dB) and keep music well under the voice.

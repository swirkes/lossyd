*Pronounced la-see-dee*

```
╔╗───────────────╔╗
║║───────────────║║
║║╔══╦══╦══╦╗─╔╦═╝║
║║║╔╗║══╣══╣║─║║╔╗║
║╚╣╚╝╠══╠══║╚═╝║╚╝║
╚═╩══╩══╩══╩═╗╔╩══╝
───────────╔═╝║
───────────╚══╝
```

# is a speculative daemon
that facilitates interactions between human and non-human entities. Currently, lossyd is centered around the [[2.4 GHz Wi-Fi Band]] and the data streams that traverse it. A couple of notes on the name lossyd:

- "d" denotes daemon, which in computer science refers to a background process that runs on a computer, often performing tasks without the user's direct involvement. A common example is a [Mailer Daemon](https://en.wikipedia.org/wiki/Bounce_message).
 - [[Daemon]] ([Ancient Greek](https://en.wikipedia.org/wiki/Ancient_Greek "Ancient Greek"): δαίμων, "god", "godlike", "power", "fate") a supernatural being working in the background as an intermediary.
 - Lossy sampling refers to compressing audio/image data and discarding some of the data to save space, resulting in lower quality but smaller files. The name is an homage to all the data that is lost in compression.

Speculation stems from the desire to fully give up control of lossyd's operation, but being unable to. Though there are programmed elements, it doesn't function as a typical computer daemon program. The possibility of a meaningful exchange between a human and the air pressure variations via audible sound is open to interpretation.

![featured image](/Images/featured.jpg)

## Implementation

A python script receives input from HackRF One, modulates the data into the audible spectrum and passes it, via OSC message, to SuperCollider.

The SuperCollider project instantiates a synth with 25 oscillators, paired with the 25 frequency bins from the HackRF One. It plays a continuous sine wave drone with tiny changes in frequency and amplitude given by the dynamic Wi-Fi signal.

The sound seems very static, however, when resonance effects are added, the microchanges in sound are amplified and more easily discerned.


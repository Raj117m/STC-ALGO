# STC ALGO

**Describe a group of buyers in one sentence. Get back what they say, what they actually do, and the gap between the two.**

STC ALGO is an open-source behavioural analysis engine. You give it one plain-language observation, such as

> *Indian teenager buys minimal phone covers every 3 weeks*

and it returns a 9-part breakdown of the people behind that behaviour and the market around them. It's built for small sellers and first-time founders who can't pay a research agency for consumer insight.

## What you get

| # | Section | What it answers |
|---|---------|-----------------|
| 1 | Persona | What this person says about themselves, in their own voice |
| 2 | Hidden signal | The fear or desire they don't say out loud |
| 3 | Behavioural record | What they actually do, and where it contradicts 1 and 2 |
| 4 | Power map | Who controls price, distribution and attention in this market |
| 5 | Broken promise | Where the market fails the buyer and why they churn |
| 6 | Money clock | When money moves: cycles, novelty decay, repeat purchase timing |
| 7 | Friction | The exact moments where intent turns into inaction |
| 8 | Unseen lever | The hidden social or identity mechanism really driving decisions |
| 9 | Entry code | The opening this leaves for a new business |

[`test_output.json`](test_output.json) is a full example result for high-income parents buying organic baby food in South Mumbai.

> ⚠️ **Known limitation:** the numbers in a report are written by the language model and **are not yet sourced**. Treat them as hypotheses to check, not facts. Grounding every statistic in a cited public source is the top item on the roadmap.

## How it works

There are two engines in this repo:

**1. `app.py`: the web app (fast).** A Flask server that sends your sentence to open Llama models on [Groq](https://groq.com) in three passes (sections 1–3, 4–6, 7–9) and stitches the result into slides with stat cards, comparison bars and timelines. The UI is `index.html`.

**2. `pipeline_v5/`: the 8-step research pipeline (deep).** Instead of one prompt, it breaks the analysis into steps that build on each other, pulling in web search results along the way:

1. **Intent processing**: work out what the observation is really about
2. **Intent cluster**: define the group of people who share it
3. **Conscious expressions**: what they *say* (beliefs, stated values)
4. **Tangible footprints**: what they *do* (purchases, habits, traces)
5. **Tension detection**: where saying and doing pull against each other. It keeps only the near-contradictions, not the obvious alignments or the total opposites, and writes a research question for each
6. **Pattern compression**: compress the tensions into behavioural signatures
7. **Refinement loop**: test and evolve the cluster against those signatures
8. **Final output**: an executive briefing

It tries Groq, Gemini and OpenAI in turn, so one rate limit doesn't stop a run.

## Run it yourself

Python 3.10+.

```bash
git clone https://github.com/Raj117m/STC-ALGO.git
cd STC-ALGO
cp .env.example .env        # then put your own key in .env
```

You need a Groq API key (free tier available): https://console.groq.com/keys

**Web app**

```bash
pip install -r requirements.txt
python app.py               # open http://localhost:5010
```

Or call the API directly:

```bash
curl -X POST http://localhost:5010/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Indian teenager buys minimal phone covers every 3 weeks"}'
```

**8-step pipeline**

```bash
pip install -r pipeline_v5/requirements.txt
python pipeline_v5/app.py   # UI at http://127.0.0.1:5005
# or from the command line:
python pipeline_v5/run_pipeline.py "Indian teenager buys minimal phone covers every 3 weeks"
```

## Roadmap

- [ ] **Cited statistics.** Every number linked to a public source, and unsourced claims clearly labelled
- [ ] **One engine.** Merge the 8-step pipeline into the web app behind a single API
- [ ] **Tests** for each pipeline step, and CI
- [ ] **Run with local open models** so it costs nothing to use
- [ ] One-command setup, docs, and a gallery of example reports
- [ ] Contributor guide and labelled starter issues

## Contributing

Issues and pull requests are welcome, especially example inputs where the analysis gets something wrong. Please never commit API keys: they belong in `.env`, which is git-ignored.

## License

[MIT](LICENSE), built by [ATOMZ](https://atomz.online).

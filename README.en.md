# Contoso Energia on Microsoft Fabric: twelve demo scenarios

Polish version: [README.md](README.md). All scenario documentation is written in Polish.

Twelve presentation-ready **Microsoft Fabric** demo scenarios for Contoso Energia,
a fictional Polish energy group organised in five segments: generation (conventional
and renewable), networks, retail, district heating and shared services (IT and platform). Each scenario
starts from one business question a board member could ask and walks through a
complete Fabric solution: data ingestion, processing, a semantic model, a report,
alerts, an app with write-back and a Data Agent.

> **Disclaimer.** This is demo material. Contoso Energia is a fictional company and
> every dataset in this repository is synthetic, generated procedurally with a fixed
> seed. Company names, sites, assets, locations and all figures are invented and do not
> describe any real enterprise. The repository is not affiliated with, endorsed by or
> based on data from any real energy company. Only general industry and regulatory
> context (described in `_program/DOMENA.md`) refers to the real world.

## Scenarios

| Folder | Business unit | Question |
|---|---|---|
| `ce-wytw-transformacja` | Generation | What happens to land and assets after coal units shut down, and what does the delay cost? |
| `ce-wytw-oze-prognoza-bess` | Generation (renewables) | How much will we produce tomorrow and when is storing better than selling? |
| `ce-wytw-oze-utrzymanie` | Generation (renewables) | Which machine fails next and can we service it before the season? |
| `ce-sieci-grid-control` | Networks | What is happening in the grid now, what will break and how to reconfigure? |
| `ce-sieci-asset-management` | Networks | Where should replacement capex go to actually reduce outage minutes? |
| `ce-sieci-meter-analytics` | Networks | Where do energy losses and voltage quality issues come from? |
| `ce-sprzedaz-customer-ops` | Retail | Why do customers call, and what can be fixed before they do? |
| `ce-sprzedaz-platforma-klienta` | Retail | How can a customer become a source of demand flexibility? |
| `ce-sprzedaz-popyt-portfel` | Retail | How much energy to buy and when, so forecast error does not become a loss? |
| `ce-uslugi-platforma-ai` | Shared services | How to run one data and AI platform for the group, and who pays for it? |
| `ce-cieplo-smart-heat` | District heating | How to produce the same heat cheaper and with lower emissions? |
| `ce-sieci-linie-vision` | Networks | Which overhead line section needs repair before a failure cuts off customers? |

`ce-uslugi-platforma-ai` is horizontal: it describes the shared platform, data catalog,
data contracts, agent factory and cost chargeback. The other eleven are vertical and assume
that platform exists. All scenarios share the model year 2026, domain dictionaries and
geography, but each one runs on its own.

## Repository layout

```
<scenario>/
├── README.md              goal, key result, assumptions and limitations
├── DEMO_SCRIPT.md         talk track, click path, fallback plan
├── SETUP_FABRIC.md        step-by-step Fabric setup
├── ARCHITECTURE.md        design decisions and Mermaid diagram
├── DATA_MODEL.md          data dictionary
├── generate_datasets.py   synthetic data generator (seed 42)
├── simulate_realtime.py   stream simulator (scenarios with a real-time layer)
├── datasets/derived/      precomputed results quoted in the documentation
├── notebooks/             Fabric notebooks as .py files with # CELL markers
├── kql/                   Eventhouse schemas, update policies, dashboard queries
├── semantic-model/        model description and DAX measures
├── report/                Power BI report specification
├── fabric-app/            app screens, fields, actions and write-back
├── activator/             alert rules and queries
└── ai/                    Data Agent sources, instructions and refusal boundaries
```

`_program/` holds the cross-scenario conventions, the domain glossary, the list of open
gaps and questions, and helper tools. `docx/` contains Word exports of the Polish
documentation: one file per document plus a combined document with a table of contents.

## Requirements

- Python 3.11 or newer. Each scenario lists its packages in `requirements.txt`
  (pandas, numpy, scikit-learn, and depending on the scenario scipy, networkx, pyarrow,
  azure-eventhub).
- A Microsoft Fabric workspace on a Fabric capacity to deploy the scenarios. Running the
  generators and notebooks locally does not need Fabric.
- Optional: an Eventstream or Event Hubs endpoint for `simulate_realtime.py`, and
  [Pandoc](https://pandoc.org/) to rebuild the Word documents.

## Getting started

```powershell
cd <scenario>
pip install -r requirements.txt
python generate_datasets.py                       # recreate raw synthetic data in datasets/
python notebooks/01_<first_notebook>.py           # recompute the derived layer
python simulate_realtime.py --dry-run --speed 60  # if the scenario has a real-time layer
```

Then follow `SETUP_FABRIC.md`: workspace, Lakehouse or Eventhouse, KQL, notebooks,
semantic model and report, Activator, Data Agent and the Fabric app.

Copy `config.example.json` to `config.json` and fill in your own workspace, capacity and
connection values. `config.json` is ignored by git; never commit real identifiers or keys.

Raw data is not stored in the repository (about 2.5 GB in total) because the generators
recreate it deterministically. `datasets/derived/` is kept because the numbers in the
documentation point to it. For `ce-uslugi-platforma-ai` the derived layer is not committed
and is produced by running the generator and notebooks.

To rebuild the Word documents:

```powershell
python _program/tools/export_docx.py
```

The script looks for Pandoc in the `PANDOC` environment variable, on `PATH`, or in the
default install folder.

## Limitations

- Models are demonstrations calibrated on synthetic data. Their quality says nothing about
  performance on real data.
- Monetary benefits are not quantified where the data does not justify it.
- No performance tests on production-scale volumes were run.
- Integration with specific versions of source systems was not modelled.

## License

MIT, see [LICENSE](LICENSE).

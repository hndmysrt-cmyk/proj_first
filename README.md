# proj_first

Arabic Flask web app for estimating electrical energy consumption from simple user inputs.

Live static site:

```text
https://hndmysrt-cmyk.github.io/proj_first/
```

## What it does

- Registers a user session.
- Collects prediction inputs: date, temperature, workday flag, and device count.
- Shows a processing screen.
- Renders a prediction result in kWh with a simple MAE indicator.
- Keeps compatibility routes for the original screen names: `sc1.html` through `sc5.html`.

The current prediction logic is a deterministic demo formula. It is ready to be replaced with a trained LSTM model when the dataset and model files are available.

## GitHub Pages

GitHub Pages serves the static files in the repository root: `index.html`, `sc1.html`, `sc2.html`, `sc3.html`, `sc4.html`, `sc5.html`, and `static/`.

The Flask app still works locally from the Jinja templates in `templates/`.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5057
```

Open:

```text
http://127.0.0.1:5057/
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

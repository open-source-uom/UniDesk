# UniDesk

UniDesk is the welcome application that ships with UniOS, a custom Linux distribution built for students and staff for all greek universities. It gives users a friendly starting point when they boot into the system, with quick access to information about the project, useful links, and the people behind it.

## What it does

When you open UniDesk you land on a simple screen with a two column layout. On the left you have introductory pages like Features, Links, and FAQ. On the right you have community oriented pages like Source Code, Contribute, and Credits. Clicking any button takes you to a dedicated page, and a back button always brings you home.

## Requirements

Python 3.10 or newer and PyQt6.

```
pip install -r requirements.txt
```

## Running it

Set up a virtual environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

Then run:

```bash
unidesk
```

## Running the tests

```bash
pip install -e ".[dev]"
QT_QPA_PLATFORM=offscreen python -m pytest
```

Tests never touch your real `~/.unios` or `~/.config/autostart`; `tests/conftest.py` redirects both into a temp dir. CI runs the same command on every PR.

## Project structure

```
src/unidesk/
    main.py                   entry point
    helpers/
        text_data.py          loads the text below from the bundled JSON
        academic_config.py    reads/writes the shared academic profile
        autostart.py          manages launching UniDesk at login
    ui/
        main_window.py        main window and all navigation logic
        widgets.py            shared widget helpers
        pages/                builders for each page (text, links, credits, academic config)
    styles/
        loader.py             loads the bundled .qss stylesheets and assets
        check.svg             checkmark icon for checkboxes
        widgets/
            controls.qss      buttons, checkbox and combo box roles
            labels.qss        label text roles
            layout.qss        backgrounds for windows, bars, cards and dividers
    assets/text_data/
        pages.json            body text for each informational page
        faq.json              FAQ entries as question/answer pairs
        credits.json          list of contributors
        links.json            external links shown in the Links page
        navigation.json       nav button labels and footer links
        ui_strings.json       buttons, titles and other interface text
        academic_institutions.json  known universities and their departments
tests/
    conftest.py               isolates $HOME and helper paths per test
    test_academic_config.py   load/save of ~/.unios/academicConfig.json
    test_autostart.py         autostart override on/off
    test_text_data.py         JSON validity, nav/page mapping, ui_strings keys, links
    test_styles.py            .qss loading and asset resolution
    test_ui.py                offscreen smoke tests for the main window and config page
```

All user-facing text lives in `assets/text_data/`. To update page content edit `pages.json`; to add a contributor edit `credits.json`. No Python changes are needed to change copy, but update every language when you do (see Translations).

## Translations

UniDesk supports English and Greek (`SUPPORTED` in `helpers/text_data.py`). Translatable strings in `assets/text_data/*.json` are stored inline, one entry per language:

```json
"back_button": { "en": "← Back", "el": "← Πίσω" }
```

The top-left button on the main page switches language and remembers the choice in `~/.config/unidesk/settings.json`. At startup the language comes from `UNIDESK_LANG` (`en` or `el`), then that saved choice, then `LANGUAGE`, `LC_ALL`, `LC_MESSAGES` and `LANG`. Anything else falls back to English, and so does a missing translation.

- Page ids (`"Introduction"`, `"FAQ"`, ...) are stable keys and are never translated. Their display titles live under `titles` in `navigation.json`.
- Names, URLs and `academic_institutions.json` are not translated: the saved university and department must stay in sync with the other UniOS apps.
- To add a language, add its code to `SUPPORTED` in `helpers/text_data.py` and add it to every `{ "en": ..., "el": ... }` entry. `tests/test_text_data.py` fails if any entry is missing a language.

## Academic profile

The footer on the home screen has a **Configure UniOS** button. It opens a page where you pick your university and department from dropdowns, which is saved to `~/.unios/academicConfig.json`. Other UniOS apps (such as UniBackpack) read this file, so the available choices live in `assets/text_data/academic_institutions.json` and must stay in sync with those apps. If UniBackpack adds new universities or departments, mirror them in `assets/text_data/academic_institutions.json`.

## Contributing

Contributions are welcome. If you want to improve the UI, fix a typo, or add a new page, open a pull request on GitHub. If you find a bug, open an issue. There is no contribution too small.

Built by Open Source UoM 2026

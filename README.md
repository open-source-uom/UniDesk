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

## Project structure

```
src/unidesk/
    main.py                   entry point
    home.py                   main window and all navigation logic
    text_data.py              loads the text below from the bundled JSON
    academic_config.py        reads/writes the shared academic profile
    assets/text_data/
        pages.json            body text for each informational page
        faq.json              FAQ entries as question/answer pairs
        credits.json          list of contributors
        links.json            external links shown in the Links page
        navigation.json       nav button labels and footer links
        ui_strings.json       buttons, titles and other interface text
        academic_institutions.json  known universities and their departments
```

All user-facing text lives in `assets/text_data/`. To update page content edit `pages.json`; to add a contributor edit `credits.json`. No Python changes are needed to change copy.

## Academic profile

The footer on the home screen has a **Configure UniOS** button. It opens a page where you pick your university and department from dropdowns, which is saved to `~/.unios/academicConfig.json`. Other UniOS apps (such as UniBackpack) read this file, so the available choices live in `assets/text_data/academic_institutions.json` and must stay in sync with those apps. If UniBackpack adds new universities or departments, mirror them in `assets/text_data/academic_institutions.json`.

## Contributing

Contributions are welcome. If you want to improve the UI, fix a typo, or add a new page, open a pull request on GitHub. If you find a bug, open an issue. There is no contribution too small.

Built by Open Source UoM 2026

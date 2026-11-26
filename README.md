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
        ann_fetcher.py        fetches, parses and caches the announcement
        academic_config.py    reads/writes the shared academic profile
        autostart.py          manages launching UniDesk at login
    ui/
        main_window.py        main window and all navigation logic
        announcements_page.py builder for the announcements page
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
        announcements.json    bundled fallback announcement
        academic_institutions.json  known universities and their departments
tests/
    conftest.py               isolates $HOME and helper paths per test
    test_academic_config.py   load/save of ~/.unios/academicConfig.json
    test_autostart.py         autostart override on/off
    test_announcements.py     announcement parsing, cache and fetcher behaviour
    test_text_data.py         JSON validity, nav/page mapping, ui_strings keys, links
    test_styles.py            .qss loading and asset resolution
    test_ui.py                offscreen smoke tests for the main window and config page
```

All user-facing text lives in `assets/text_data/`. To update page content edit `pages.json`; to add a contributor edit `credits.json`. No Python changes are needed to change copy.

## Academic profile

The footer on the home screen has a **Configure UniOS** button. It opens a page where you pick your university and department from dropdowns, which is saved to `~/.unios/academicConfig.json`. Other UniOS apps (such as UniBackpack) read this file, so the available choices live in `assets/text_data/academic_institutions.json` and must stay in sync with those apps. If UniBackpack adds new universities or departments, mirror them in `assets/text_data/academic_institutions.json`.

## Announcements

The home screen has an **Announcements** row below the navigation grid. It opens a page showing one announcement at a time, with its title, publication date and body. The page reads the cached copy from `~/.unios/unidesk/announcements.json` when it is built, falls back to `assets/text_data/announcements.json`, and shows a muted empty-state line when neither is available. At startup UniDesk fetches the latest version from the project site once; network or parsing failures are ignored, and the fetched copy is cached for the next launch.

## Contributing

Contributions are welcome. If you want to improve the UI, fix a typo, or add a new page, open a pull request on GitHub. If you find a bug, open an issue. There is no contribution too small.

Built by Open Source UoM 2026

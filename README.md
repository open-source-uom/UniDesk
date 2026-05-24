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

```
python src/unidesk/main.py
```

## Project structure

```
src/unidesk/
    main.py       entry point
    home.py       main window and all navigation logic
    pages.py      text content for each informational page
    credits.py    list of contributors
    links.py      external links shown in the Links page
```

To update any page content just open `pages.py` and edit the body text for that page. To add a new contributor open `credits.py`.

## Contributing

Contributions are welcome. If you want to improve the UI, fix a typo, or add a new page, open a pull request on GitHub. If you find a bug, open an issue. There is no contribution too small.

Built by Open Source UoM 2026

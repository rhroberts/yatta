# yatta

Yet Another Time Tracking App

## Install

```bash
pip install yatta
```

## Development

- [Install poetry](https://python-poetry.org/docs/#installation)
- Get source and install dependencies
    ```bash
    git clone https://github.com/rhroberts/yatta
    cd yatta
    poetry install
    ```
- Open a shell within the poetry-managed virtual environment: `poetry shell` 

Alternatively, you can manually install the dependencies in [pyproject.toml](https://github.com/rhroberts/yatta/blob/master/pyproject.toml) and use the development environment of your choice.


## Usage

yatta is a stopwatch-style time tracker that stores task information and provides some reporting and visualization tools.

There are two main components of yatta: *tasks* and *records*. Tasks are what you track. They are unique and reusable. Information about tracked tasks are stored as records. In general, the format of a yatta command is `yatta [VERB] [NOUN]`. Tasks and records are nouns. The verbs are the commands `track`, `list`, `edit`, `delete`, etc. The `track` command is specific to tasks, but all other commands can be applied to both tasks and records.

#### Track a task

```bash
yatta track paperwork  # start a stopwatch to track the task `paperwork`
yatta track "finish my masterpiece"
```

#### List tasks and records

```bash
yatta list task  # list all tasks
yatta list task paperwork  # show info for task 'paperwork'
yatta list record  # list recent records
yatta list record paperwork  # list x tj records for the task 'paperwork'
```

#### Edit tasks and records

```bash
yatta edit task paperwork # edit info about the paperwork task in default $EDITOR
```

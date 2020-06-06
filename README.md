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

There are two main components of yatta: *tasks* and *records*. Tasks are what you track. They are unique and reusable. Information about tracked tasks are stored as records. In general, the format of a yatta command is `yatta [COMMAND] [TASKS/RECORDS] [FILTER]`. For example, the command `yatta list records -t "Write README.md"` lists all records for the task "Write README.md". The `track` command is the main exception to this format, and it is specific to tasks. All other commands can be applied to both tasks and records.

#### Track a task

```bash
yatta track "Write README.md"  # start a stopwatch to track the task "Write README.md"
```

#### List tasks and records

```bash
yatta list tasks  # list all tasks
yatta list tasks "Write README.md"  # show info for task "Write README.md"
yatta list records  # list recent records
yatta list records -t "Write README.md"  # list records for the task "Write README.md"
yatta list records -t 12  # list records for task with id=12
```

#### Edit tasks and records

```bash
yatta edit task "Write README.md" # edit info about the "Write README.md" task in default $EDITOR
yatta edit task 8 -d "water the plants"  # add a description to task with id=8 
```

#### Delete tasks and records

```bash
yatta delete task plants  # remove task "plants" and all its records from database
yatta delete record 4  # remove record with id=4 from the database
```

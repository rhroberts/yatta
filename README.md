# yatta

Yet Another Time Tracking App

## Install

```bash
git clone https://github.com/rhroberts/yatta.git
sudo ln -s /path/to/yatta/yatta /usr/local/bin/yatta  # or somewhere else in your $PATH
```

Then create `.yattarc` in your home directory. An example file is given [here](./.yattarc).

## Usage

`yatta [TASK] [TAGS]`

- TASK is case-insensitive
- TAGS should be of the form `tag` or `tag1/tag2/tag3`
  - `yatta exercise personal/fitness`
  - `yatta "take out the trash" chores/personal/todo`
  

# trestle-bot

trestle-bot assists users in leveraging [Compliance-Trestle](https://github.com/IBM/compliance-trestle) in automated workflows or [OSCAL](https://github.com/usnistgov/OSCAL) formatted compliance content management. 

In addition to trestle-bot, this repo contains the trestle-bot GitHub Action that can optionally be used to host the tresle-bot service within GitHub Actions.

> WARNING: This project is under active development.

## Usage

trestle-bot supports the following commands:

### `/assemble`
Converts repo defined markdown formatted OSCAL content to JSON.


### `/help`
Displays help information for trestle-bot.

## Contributing

### Format and Styling

```
make format
make lint
```

### Running tests
```
make test
```

### Run with poetry
```
poetry run trestle-bot
```
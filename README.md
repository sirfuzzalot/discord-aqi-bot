# Discord AQI Bot

Discord AQI Bot sends AQI data on the interval you provide to your Discord channel.
This includes current AQI data and forecast data for the zip code provided.

```
🥞 Saturday Morning 🍳 ↴

Current AQI
-------------------------------
Recorded: 2020-11-07 07:00:00-08:00
Location: E San Fernando Vly

      O3  |  39
   PM2.5  |  23

Forecast AQI
-------------------------------
Forecast For: 2020-11-07
Location: E San Fernando Vly

      O3  |  38
     NO2  |  21
   PM2.5  |  42
    PM10  |  20
```

To everyone giving this application a try, please keep in mind that AWS
does have associate costs and **you are responsible for any costs you incur**.

## Installation

You will need the following:

1. AWS account

2. [Serverless Framework](https://www.serverless.com/) account

3. [Node.js](https://nodejs.org/en/download/)

4. (optional) Python 3.8 and Git

To wrap up your installations you'll want to install the Serverless
requirements plugin.

```bash
cd ./discord-aqi-bot
npm install
```

## Configuration

Discord AQI Bot uses two configuration files:

`serverless.yml` - the configuration file for the Serverless Framework.

`env.json` - the majority of the values we'll be customizing.

Once you've setup a Serverless account, you should create an app in
the Serverless web UI. Now we'll make a copy of the `template.serverless.yml`
file and rename it to `serverless.yml` file. This file is ignored by Git.

bash

```bash
cd ./discord-aqi-bot
cp ./tools/template.serverless.yml ./serverless.yml
```

powershell

```powershell
cd .\discord-aqi-bot
Copy-Item -Path .\tools\template.serverless.yml -Destination .\serverless.yml
```

```yaml
# serverless.yml
org: # Serverless organization name. Typically your username.
app: # Serverless App name from the Serverless Web UI.
service: aqi-bot

frameworkVersion: "2"

provider:
  name: aws
  runtime: python3.8
  stage: prod
  region: # AWS region for the Lambda. Ex: us-west-2

package:
  include:
    - requirements.txt
    - handler.py
    - lib/**

functions:
  aqi-report:
    handler: handler.aqi_report
    events:
      - schedule: # Your cron expression in UTC. Ex: cron(0 1,16 * * ? *)
    memorySize: 128
    environment:
      AQI_BOT_AIRNOW_API_TOKEN: ${file(./env.json):AQI_BOT_AIRNOW_API_TOKEN}
      AQI_BOT_AIRNOW_ZIP_CODE: ${file(./env.json):AQI_BOT_AIRNOW_ZIP_CODE}
      AQI_BOT_DISCORD_BOT_URL: ${file(./env.json):AQI_BOT_DISCORD_BOT_URL}
      AQI_BOT_MORNING_RANGE_UTC: ${file(./env.json):AQI_BOT_MORNING_RANGE_UTC}

plugins:
  - serverless-python-requirements
custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
```

Be careful with the `cron` expression as it's what fires off your Lambda
function and costs you money. There is a certain amount of Lambda runtime
that AWS provides at no cost. You'll need to consult their docs for specifics.
If you want a guaranteed free option you can run this on your machine as
a cron/windows schedule event OR you can try [Kubeless](https://kubeless.io/)
(fair warning, this will involve more configuration and setup).

Next let's make a copy of the `template.env.json` file and rename it to
`env.json`.

bash

```bash
cd ./discord-aqi-bot
cp ./tools/template.env.json ./env.json
```

powershell

```powershell
cd .\discord-aqi-bot
Copy-Item -Path .\tools\template.env.json -Destination .\env.json
```

Then let's fill in the each of the values. Some of which will come from
the [AirNow API](https://docs.airnowapi.org/). For **AQI_BOT_DISCORD_BOT_URL** go to your Discord server settings > Integrations > Webhooks.

```JSON
# env.json
{
  "AQI_BOT_AIRNOW_API_TOKEN": "Your airnow.gov API token",
  "AQI_BOT_AIRNOW_ZIP_CODE": "US Postal Zip Code of the AQI data",
  "AQI_BOT_DISCORD_BOT_URL": "Discord webhook URL to send AQI data. Its a POST",
  "AQI_BOT_MORNING_RANGE_UTC": "Two integers separated by a comma that
  represent a range that is considered morning for your Discord channel.
  This affects the greeting. Integers map to 24hr UTC hours. For
  example 5:00UTC to 9:00UTC. Ex: 5,9"
}
```

## Deploying

Discord AQI Bot uses the [Serverless Framework](https://www.serverless.com/)
to make deployment into AWS infrastructure easier. Check out their
[CLI Docs for more details](https://www.serverless.com/framework/docs/providers/aws/cli-reference/).
Make sure you've completed the Installation and Configuration sections
before attempting to deploy.

Deploy all functions

```bash
cd ./discord-aqi-bot
serverless deploy
```

Remove all functions

```bash
cd ./discord-aqi-bot
serverless remove
```

As a special note, this repo has been setup for manual deployment from
your local machine. If you plan to use this repo with a CI/CD system
you may have to adjust the `.gitignore` to keep the `serverless.yml`
and save your ENV values in your CI/CD system.

## Logs and Testing

Discord AQI Bot will log to AWS Cloud Watch. You can test the deployed function
either by changing the `cron` and redploying or by going to the AWS Lambda
web UI (AWS Console) and running a test. Check the AWS docs for more on
testing Lambda functions.

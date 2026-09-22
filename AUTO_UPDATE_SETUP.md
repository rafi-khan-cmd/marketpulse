# Scheduling daily updates

The dashboard is only as useful as its most recent data, so `update_marketpulse` should run once a day. The simplest way to do this on a free host is to hit the update endpoint from a hosted cron service.

## Using a hosted cron service

The app exposes an update endpoint that runs the full pipeline:

```
POST https://marketpulse-production-a407.up.railway.app/api/update/
```

The endpoint is protected: it only accepts `POST`, and the request must carry an
`X-Update-Token` header whose value matches the `UPDATE_API_TOKEN` environment
variable set on the server. Set `UPDATE_API_TOKEN` to a long random string in
your host's variables before scheduling. A second request while an update is
already running returns `429` instead of starting a duplicate run.

With [cron-job.org](https://cron-job.org) (free):

1. Create an account and add a new cronjob.
2. Set the address to the update endpoint above and the method to `POST`.
3. Add a request header `X-Update-Token` with the same value as `UPDATE_API_TOKEN`.
4. Schedule it daily, ideally around 06:00 UTC when markets are closed and the previous day's data is settled.

[EasyCron](https://www.easycron.com) and [UptimeRobot](https://uptimerobot.com) work the same way (POST + custom header).

## What the update does

Each run refreshes:

- Market data (SPX, VIX, volume)
- Economic indicators (CPI, unemployment, rates)
- News articles with sentiment and topic tags
- The retrained direction model
- All charts and predictions on the dashboard

## Checking it worked

Wait for the scheduled time and confirm the dashboard shows fresh data, or hit the update endpoint directly. If it isn't running, check the cron service's execution log and the Railway logs, and confirm the API keys are set on the service.

## Running it locally instead

On a machine that's always on, `setup_scheduled_updates.sh` installs a local cron entry that calls `python manage.py update_marketpulse` on a schedule.

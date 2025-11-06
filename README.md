# metrics-monitoring-exercise


## The task

```
Python Utility Script
Goal: Assess development and scripting skills common in DevOps.
Example task:
Write a Python or Bash script that:
- Checks the disk usage on a list of remote servers (given by IPs).
- Warns if usage exceeds 80%.
- Sends an alert (email or Slack webhook).

Evaluation points:
- API usage (Slack, SMTP, etc.)
- Logging
- Error handling
- Clean, modular code
```

## What I did

- Implemented a configurable Python script that iterates over a list of IPs and queries disk usage via SSH.
- Implemented with an object-oriented approach for better extensibility and maintainability.

## Features

- SSH connections using the paramiko package (supports password and key authentication).
- Configurable notifications (Slack, email, etc.).
- Configurable thresholds (disk usage percentage).
- Configurable check interval (check disk usage every X seconds).

## Future enhancements

- Aggregate results and send a single notification per iteration for better scalability.
- Make the disk usage query method and target mount configurable (we may not always want to query /).
- Add retries, backoff, and richer error reporting for transient SSH failures.
- Add support for parallel checks to improve performance on large host lists.

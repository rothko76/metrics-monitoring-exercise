import os
import json
import time
import logging
import requests
import paramiko
from abc import ABC, abstractmethod
from typing import List, Dict

# -------------------- Configuration --------------------
class Config:
    def __init__(self, config_file: str = None):
        # Default configuration
        self.servers = ["192.168.1.10", "192.168.1.11"]
        self.threshold = 80  # percent
        self.interval = 60  # seconds
        self.log_level = "INFO"
        self.notification_type = "slack"  # or 'email'
        self.notification_config = {
            "slack_webhook_url": "http://localhost:5000/notify",
            "email": {"smtp_server": "", "from_addr": "", "to_addrs": []}
        }

        # Override from JSON file if provided
        if config_file and os.path.exists(config_file):
            with open(config_file, "r") as f:
                data = json.load(f)
                self.__dict__.update(data)

    def to_string(self) -> str:
        """Return a pretty-printed JSON representation of the configuration."""
        try:
            cfg = {
                "servers": self.servers,
                "threshold": self.threshold,
                "interval": self.interval,
                "log_level": self.log_level,
                "notification_type": self.notification_type,
                "notification_config": self.notification_config,
            }
            return json.dumps(cfg, indent=2, sort_keys=True)
        except Exception:
            return str(self.__dict__)

    def __str__(self) -> str:
        return self.to_string()


# -------------------- Logging --------------------
def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

# -------------------- Notifier Interface --------------------
class Notifier(ABC):
    @abstractmethod
    def notify(self, message: str):
        pass

# Slack Notifier
class SlackNotifier(Notifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify(self, message: str):
        try:
            response = requests.post(self.webhook_url, json={"text": message})
            response.raise_for_status()
            logging.info(f"Slack notification sent: {message}")
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")

# Email Notifier
class EmailNotifier(Notifier):
    def __init__(self, smtp_server: str, from_addr: str, to_addrs: List[str]):
        import smtplib
        from email.message import EmailMessage
        self.smtplib = smtplib
        self.EmailMessage = EmailMessage
        self.smtp_server = smtp_server
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    def notify(self, message: str):
        try:
            msg = self.EmailMessage()
            msg.set_content(message)
            msg["Subject"] = "Disk Usage Alert"
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)

            with self.smtplib.SMTP(self.smtp_server) as server:
                server.send_message(msg)
            logging.info(f"Email notification sent: {message}")
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")

# -------------------- Disk Checker Interface --------------------
class DiskChecker(ABC):
    @abstractmethod
    def check_disk_usage(self, server_ip: str) -> int:
        """Return disk usage percentage (0-100)"""
        pass

# SSH-based Disk Checker
class SSHDiskChecker(DiskChecker):
    def __init__(self, username: str, password: str = None, key_file: str = None):
        self.username = username
        self.password = password
        self.key_file = key_file

    def check_disk_usage(self, server_ip: str) -> int:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  
            if self.key_file:
                ssh.connect(server_ip, username=self.username, key_filename=self.key_file)
            else:
                ssh.connect(server_ip, username=self.username, password=self.password)

            stdin, stdout, stderr = ssh.exec_command("df -h / | tail -1 | awk '{print $5}'")
            usage_str = stdout.read().decode().strip()
            ssh.close()

            percent = int(usage_str.replace("%", ""))
            logging.info(f"{server_ip} disk usage: {percent}%")
            return percent
        except Exception as e:
            logging.error(f"Error checking {server_ip}: {e}")
            return -1

# -------------------- Monitor --------------------
class DiskMonitor:
    def __init__(self, servers: List[str], threshold: int, checker: DiskChecker, notifier: Notifier):
        self.servers = servers
        self.threshold = threshold
        self.checker = checker
        self.notifier = notifier

    def run_check(self):
        for server in self.servers:
            usage = self.checker.check_disk_usage(server)
            if usage >= self.threshold:
                self.notifier.notify(f'Warning: {server} disk usage at {usage}%')

# -------------------- Main --------------------
def main():
    config = Config("config.json")
    setup_logging(config.log_level)
    logging.debug(config.to_string())

    # Choose notifier
    if config.notification_type.lower() == "slack":
        notifier = SlackNotifier(config.notification_config["slack_webhook_url"])
    elif config.notification_type.lower() == "email":
        email_cfg = config.notification_config["email"]
        notifier = EmailNotifier(email_cfg["smtp_server"], email_cfg["from_addr"], email_cfg["to_addrs"])
    else:
        raise ValueError("Unsupported notifier type")
    

    # Disk checker (can easily swap for local or SNMP checker later)
    checker = SSHDiskChecker(username="")  # add password/key_file if needed

    monitor = DiskMonitor(config.servers, config.threshold, checker, notifier)
    logging.info("Starting modular disk monitor...")

    while True:
        monitor.run_check()
        time.sleep(config.interval)

if __name__ == "__main__":
    main()
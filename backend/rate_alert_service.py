"""
Rate Alert Service
Tracks API usage against configured daily limits and sends proactive alerts
before limits are reached.

Alert channels:
- Email (SMTP)
- GitHub issue creation (generates GitHub notifications for repo watchers)
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _as_bool(value: str, default: bool = False) -> bool:
	if value is None:
		return default
	return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str, default: int) -> int:
	try:
		return int(value)
	except (TypeError, ValueError):
		return default


class RateAlertService:
	def __init__(self):
		self.enabled = _as_bool(os.getenv("RATE_ALERTS_ENABLED", "true"), True)
		self.threshold_percent = _as_int(os.getenv("RATE_ALERT_THRESHOLD_PERCENT", "80"), 80)

		# Daily limits (configure these to match your provider plan limits)
		self.limits = {
			"gemini": _as_int(os.getenv("RATE_ALERT_GEMINI_DAILY_LIMIT", "1000"), 1000),
			"twilio": _as_int(os.getenv("RATE_ALERT_TWILIO_DAILY_LIMIT", "500"), 500),
			"supabase": _as_int(os.getenv("RATE_ALERT_SUPABASE_DAILY_LIMIT", "5000"), 5000),
			"s3": _as_int(os.getenv("RATE_ALERT_S3_DAILY_LIMIT", "1000"), 1000),
		}

		self.current_day = self._today_utc()
		self.usage_counts = {service: 0 for service in self.limits}
		self.alerted_today = set()

	@staticmethod
	def _today_utc() -> str:
		return datetime.now(timezone.utc).date().isoformat()

	def _reset_if_new_day(self):
		today = self._today_utc()
		if today != self.current_day:
			self.current_day = today
			self.usage_counts = {service: 0 for service in self.limits}
			self.alerted_today.clear()
			logger.info("RateAlertService counters reset for new UTC day")

	def track_usage(self, service: str, increment: int = 1, context: str = ""):
		"""
		Increment service usage and trigger alert if threshold is reached.

		Args:
			service: one of gemini/twilio/supabase/s3
			increment: amount to increment
			context: optional context string for alert message
		"""
		if not self.enabled:
			return

		self._reset_if_new_day()

		if service not in self.limits:
			logger.debug(f"Unknown service '{service}' for rate tracking")
			return

		limit = self.limits.get(service, 0)
		if limit <= 0:
			return

		self.usage_counts[service] += max(0, increment)
		used = self.usage_counts[service]
		usage_percent = round((used / limit) * 100, 2)

		if usage_percent >= self.threshold_percent and service not in self.alerted_today:
			title = f"[SwasthaLink] {service.upper()} usage at {usage_percent}%"
			body = self._build_alert_body(
				service=service,
				used=used,
				limit=limit,
				usage_percent=usage_percent,
				context=context,
			)

			self._send_alerts(title=title, body=body)
			self.alerted_today.add(service)
			logger.warning(
				f"Rate alert triggered for {service}: {used}/{limit} ({usage_percent}%)"
			)

	def _build_alert_body(
		self,
		service: str,
		used: int,
		limit: int,
		usage_percent: float,
		context: str = "",
	) -> str:
		remaining = max(limit - used, 0)
		return (
			"SwasthaLink proactive rate alert\n\n"
			f"Service: {service}\n"
			f"UTC day: {self.current_day}\n"
			f"Used: {used}\n"
			f"Configured limit: {limit}\n"
			f"Usage: {usage_percent}%\n"
			f"Remaining: {remaining}\n"
			f"Threshold: {self.threshold_percent}%\n"
			f"Context: {context or 'N/A'}\n\n"
			"Action needed:\n"
			"1) Rotate/upgrade provider plan if needed\n"
			"2) Reduce request volume or cache responses\n"
			"3) Tune RATE_ALERT_*_DAILY_LIMIT values to real provider quotas\n"
		)

	def _send_alerts(self, title: str, body: str):
		self._send_email_alert(title, body)
		self._create_github_issue_alert(title, body)

	def _send_email_alert(self, title: str, body: str):
		email_enabled = _as_bool(os.getenv("RATE_ALERT_EMAIL_ENABLED", "false"), False)
		if not email_enabled:
			return

		smtp_host = os.getenv("SMTP_HOST")
		smtp_port = _as_int(os.getenv("SMTP_PORT", "587"), 587)
		smtp_username = os.getenv("SMTP_USERNAME")
		smtp_password = os.getenv("SMTP_PASSWORD")
		smtp_use_tls = _as_bool(os.getenv("SMTP_USE_TLS", "true"), True)
		from_email = os.getenv("ALERT_FROM_EMAIL")
		to_email_raw = os.getenv("ALERT_TO_EMAIL", "")
		to_emails = [x.strip() for x in to_email_raw.split(",") if x.strip()]

		required = [smtp_host, smtp_username, smtp_password, from_email]
		if not all(required) or not to_emails:
			logger.warning("Email alert enabled but SMTP/email env vars are incomplete")
			return

		try:
			msg = MIMEMultipart()
			msg["From"] = from_email
			msg["To"] = ", ".join(to_emails)
			msg["Subject"] = title
			msg.attach(MIMEText(body, "plain", "utf-8"))

			with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
				if smtp_use_tls:
					server.starttls()
				server.login(smtp_username, smtp_password)
				server.sendmail(from_email, to_emails, msg.as_string())

			logger.info("Rate alert email sent successfully")

		except Exception as exc:
			logger.error(f"Failed to send rate alert email: {exc}")

	def _create_github_issue_alert(self, title: str, body: str):
		github_enabled = _as_bool(os.getenv("RATE_ALERT_GITHUB_ENABLED", "false"), False)
		if not github_enabled:
			return

		token = os.getenv("GITHUB_TOKEN")
		owner = os.getenv("GITHUB_REPO_OWNER")
		repo = os.getenv("GITHUB_REPO_NAME")

		if not token or not owner or not repo:
			logger.warning("GitHub alert enabled but GITHUB_* env vars are incomplete")
			return

		issue_body = (
			f"## Proactive rate usage alert\n\n"
			f"{body}\n"
			"_Auto-generated by SwasthaLink RateAlertService._"
		)

		url = f"https://api.github.com/repos/{owner}/{repo}/issues"
		headers = {
			"Authorization": f"Bearer {token}",
			"Accept": "application/vnd.github+json",
			"X-GitHub-Api-Version": "2022-11-28",
		}
		payload = {"title": title, "body": issue_body, "labels": ["ops", "rate-limit-alert"]}

		try:
			response = httpx.post(url, headers=headers, json=payload, timeout=20.0)
			if response.status_code >= 300:
				logger.error(
					f"Failed to create GitHub issue alert: {response.status_code} {response.text}"
				)
			else:
				logger.info("Rate alert GitHub issue created successfully")
		except Exception as exc:
			logger.error(f"Failed to create GitHub issue alert: {exc}")

	def get_status(self) -> Dict[str, Any]:
		self._reset_if_new_day()
		status = {}
		for service, limit in self.limits.items():
			used = self.usage_counts.get(service, 0)
			percent = round((used / limit) * 100, 2) if limit > 0 else 0
			status[service] = {
				"used": used,
				"limit": limit,
				"usage_percent": percent,
				"threshold_percent": self.threshold_percent,
				"alert_sent_today": service in self.alerted_today,
			}

		return {
			"enabled": self.enabled,
			"utc_day": self.current_day,
			"services": status,
		}


rate_alert_service = RateAlertService()


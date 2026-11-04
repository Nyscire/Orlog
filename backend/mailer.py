"""Wysyłka maili (kody do resetu hasła).

Serwer pocztowy ustawiają zmienne środowiskowe:
  ORLOG_SMTP_HOST       np. smtp.gmail.com; bez niej maile trafiają tylko do logu serwera
  ORLOG_SMTP_PORT       domyślnie 587 (465 przy ORLOG_SMTP_SECURITY=ssl)
  ORLOG_SMTP_SECURITY   starttls (domyślnie), ssl albo none
  ORLOG_SMTP_USER, ORLOG_SMTP_PASSWORD
  ORLOG_SMTP_FROM       nadawca, domyślnie ORLOG_SMTP_USER

Bez skonfigurowanej poczty treść maila (z kodem) widać w logu serwera, więc
administrator może przekazać kod graczowi sam.
"""
from __future__ import annotations

import logging
import os
import smtplib
import threading
from email.message import EmailMessage
from typing import Callable, Dict, Optional

log = logging.getLogger(__name__)


class Mailer:
    def __init__(self, env: Optional[Dict[str, str]] = None,
                 run: Callable[[Callable[[], None]], None] | None = None) -> None:
        env = os.environ if env is None else env
        self.host = env.get("ORLOG_SMTP_HOST", "").strip()
        self.security = env.get("ORLOG_SMTP_SECURITY", "starttls").strip().lower() or "starttls"
        default_port = "465" if self.security == "ssl" else "587"
        self.port = int(env.get("ORLOG_SMTP_PORT", "").strip() or default_port)
        self.user = env.get("ORLOG_SMTP_USER", "").strip()
        self.password = env.get("ORLOG_SMTP_PASSWORD", "")
        self.sender = env.get("ORLOG_SMTP_FROM", "").strip() or self.user or "orlog@localhost"
        # wysyłka nie blokuje obsługi gracza: domyślnie w osobnym wątku
        self.run = run or (lambda job: threading.Thread(target=job, daemon=True).start())

    @property
    def configured(self) -> bool:
        return bool(self.host)

    def send(self, to: str, subject: str, body: str) -> None:
        if not self.configured:
            log.warning("Poczta nie jest skonfigurowana (ORLOG_SMTP_HOST). Mail do %s:\n%s\n%s", to, subject, body)
            return
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        self.run(lambda: self._deliver(message))

    def _deliver(self, message: EmailMessage) -> None:
        try:
            if self.security == "ssl":
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=20)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=20)
            with server:
                if self.security == "starttls":
                    server.starttls()
                if self.user:
                    server.login(self.user, self.password)
                server.send_message(message)
            log.info("Wysłano mail do %s", message["To"])
        except Exception as err:   # zła konfiguracja nie może położyć serwera gry
            log.error("Nie udało się wysłać maila do %s: %s", message["To"], err)

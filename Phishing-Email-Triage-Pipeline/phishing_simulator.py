#!/usr/bin/env python3
"""
Phishing Email Simulator
Generates realistic fake phishing email logs in JSON format
for Splunk ingestion and SOC automation testing.
"""

import json
import random
import string
import argparse
import time
import os
from datetime import datetime, timezone

# ─────────────────────────────────────────────
#  REAL MALICIOUS HASHES (from MalwareBazaar)
# ─────────────────────────────────────────────

MALICIOUS_SAMPLES = [
    {
        "name": "eicar_test.com",
        "hash": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
        "family": "EICAR-Test-File",
        "type": "Test File"
    },
    {
        "name": "Account_Verification.pdf",
        "hash": "b80b4afd8745f9e06a9358cf8fc9769771fc05cbf8ec5399ba32cca85240d68e",
        "family": "FormBook",
        "type": "PDF"
    },
]
# ─────────────────────────────────────────────
#  PHISHING SCENARIOS
# ─────────────────────────────────────────────

SCENARIOS = {
    "credential_harvest": {
        "subjects": [
            "Urgent: Your account password will expire in 24 hours",
            "Action Required: Verify your Microsoft account",
            "Security Alert: Unusual sign-in activity detected",
            "Your OneDrive storage is full - verify now",
            "IT Department: Mandatory password reset required",
        ],
        "sender_names": ["IT Support", "Microsoft Security", "Account Team", "Helpdesk"],
        "spoofed_domains": ["microsoftt.com", "micros0ft.com", "microsoft-security.com", "ms-support.net"],
        "legit_domain": "microsoft.com",
        "urls": [
            "http://malware.testing.google.test/testing/malware/",
            "http://testsafebrowsing.appspot.com/s/phishing.html",
            "http://www.eicar.org/download/eicar.com",
        ],
        "body_snippets": [
            "Your password will expire soon. Click the link below to update your credentials immediately to avoid losing access.",
            "We detected suspicious login from Russia. Verify your identity immediately or your account will be suspended.",
            "Your Microsoft 365 license requires immediate verification. Failure to verify will result in account termination.",
        ],
        "spam_score_range": (0.85, 0.99),
        "dkim": "fail",
        "spf": "fail",
        "dmarc": "fail",
    },
    "invoice_fraud": {
        "subjects": [
            "Invoice #INV-2026-0523 Payment Required",
            "URGENT: Overdue invoice - immediate payment needed",
            "Your invoice from Accounting Department",
            "Final Notice: Payment overdue - account suspension pending",
            "Attached: Invoice for services rendered Q1 2026",
        ],
        "sender_names": ["Accounts Payable", "Finance Department", "Billing Team", "CFO Office"],
        "spoofed_domains": ["paypa1.com", "paypal-billing.com", "invoice-secure.net", "billing-dept.org"],
        "legit_domain": "paypal.com",
        "urls": [
            "http://paypa1.com/invoice/pay",
            "http://secure-billing.paypal-support.tk/pay",
            "http://invoice.pay-now.ru/confirm",
        ],
        "body_snippets": [
            "Please find attached invoice for $4,750.00. Payment is overdue. Click to pay immediately to avoid late fees.",
            "Your account shows an outstanding balance of $12,300. Please review the attached invoice and process payment.",
            "FINAL NOTICE: Your invoice is 30 days overdue. Immediate payment required to avoid collections.",
        ],
        "spam_score_range": (0.75, 0.95),
        "dkim": "fail",
        "spf": "softfail",
        "dmarc": "fail",
    },
    "ceo_fraud": {
        "subjects": [
            "Confidential - Wire Transfer Request",
            "Urgent request from CEO",
            "Private: Need your help immediately",
            "Sensitive: Gift card purchase needed ASAP",
            "Confidential wire transfer - do not discuss",
        ],
        "sender_names": ["CEO", "John Smith - CEO", "Executive Office", "President"],
        "spoofed_domains": ["company-ceo.com", "exec-office.net", "ceo-private.org"],
        "legit_domain": "yourcompany.com",
        "urls": [],
        "body_snippets": [
            "I need you to process an urgent wire transfer of $45,000 to a new vendor. This is time-sensitive and confidential.",
            "I'm in a meeting and need you to purchase 10 x $500 Amazon gift cards immediately. Send me the codes ASAP.",
            "We are closing a deal and I need you to wire $78,500 urgently. This must be done today.",
        ],
        "spam_score_range": (0.6, 0.85),
        "dkim": "fail",
        "spf": "fail",
        "dmarc": "fail",
    },
    "malware_delivery": {
        "subjects": [
            "Your package delivery failed - action required",
            "DHL: Package #DHL29384756 delivery notification",
            "Shipping notification: Your order has shipped",
            "FedEx: Unable to deliver your package",
            "Document shared with you: Q1 Report 2026",
        ],
        "sender_names": ["DHL Delivery", "FedEx Notifications", "UPS Tracking", "Shipping Team"],
        "spoofed_domains": ["dhl-delivery.com", "fedex-tracking.net", "ups-notifications.org", "delivery-notify.ru"],
        "legit_domain": "dhl.com",
        "urls": [
            "http://dhl-delivery-confirm.ru/track",
            "http://fedex-package.pages.dev/confirm",
            "http://tracking.ups-delivery.tk/download",
        ],
        "body_snippets": [
            "Your package could not be delivered. Download the attached label and bring it to your nearest post office.",
            "DHL was unable to deliver your package. Please open the attached file to reschedule delivery.",
            "Your shipment requires customs documentation. Open the attached form and complete it within 24 hours.",
        ],
        "spam_score_range": (0.80, 0.99),
        "dkim": "fail",
        "spf": "fail",
        "dmarc": "fail",
    },
}

# ─────────────────────────────────────────────
#  HELPER DATA
# ─────────────────────────────────────────────

VICTIM_EMAILS = [
    "john.doe@company.com",
    "jane.smith@company.com",
    "admin@company.com",
    "finance@company.com",
    "hr@company.com",
    "it.support@company.com",
    "ceo@company.com",
    "accounting@company.com",
]

MAIL_SERVERS = [
    "mail.microsoftt.com",
    "smtp.paypa1.com",
    "mx1.evil-domain.ru",
    "relay.phish-server.tk",
    "outbound.spam-host.net",
    "mail.fake-company.org",
]

ATTACKER_IPS = [
    "185.220.101.45",
    "194.165.16.78",
    "45.142.212.100",
    "91.108.4.0",
    "103.87.68.194",
    "77.83.36.42",
]


def random_message_id():
    chars = string.ascii_lowercase + string.digits
    local = ''.join(random.choices(chars, k=12))
    domain = ''.join(random.choices(chars, k=8)) + ".com"
    return f"<{local}@{domain}>"


def generate_phishing_email(scenario_name=None):
    if scenario_name is None or scenario_name == "all":
        scenario_name = random.choice(list(SCENARIOS.keys()))

    scenario = SCENARIOS[scenario_name]

    # Sender
    spoofed_domain = random.choice(scenario["spoofed_domains"])
    sender_name = random.choice(scenario["sender_names"])
    sender_local = sender_name.lower().replace(" ", ".").replace("-", "")
    sender_email = f"{sender_local}@{spoofed_domain}"

    # Recipient
    recipient = random.choice(VICTIM_EMAILS)

    # Subject & body
    subject = random.choice(scenario["subjects"])
    body_snippet = random.choice(scenario["body_snippets"])

    # Link
    has_link = len(scenario["urls"]) > 0
    link_url = random.choice(scenario["urls"]) if has_link else ""

    # ── ALWAYS has attachment with real malicious hash ──
    sample = random.choice(MALICIOUS_SAMPLES)
    attachment_name = sample["name"]
    attachment_hash = sample["hash"]
    attachment_size = random.randint(15000, 2500000)
    malware_family = sample["family"]
    attachment_type = sample["type"]

    # Spam score
    spam_score = round(random.uniform(*scenario["spam_score_range"]), 4)

    # Network
    sender_ip = random.choice(ATTACKER_IPS)
    mail_server = random.choice(MAIL_SERVERS)

    ts = datetime.now(timezone.utc).isoformat()

    event = {
        "timestamp": ts,
        "scenario": scenario_name,
        "message_id": random_message_id(),
        "from": sender_email,
        "to": recipient,
        "subject": subject,
        "body_snippet": body_snippet,
        "sender_domain": spoofed_domain,
        "sender_ip": sender_ip,
        "mail_server": mail_server,
        "has_link": str(has_link).lower(),
        "link_url": link_url,
        "has_attachment": "true",
        "attachment_name": attachment_name,
        "attachment_hash_sha256": attachment_hash,
        "attachment_size_bytes": attachment_size,
        "malware_family": malware_family,
        "attachment_type": attachment_type,
        "authentication_spf": scenario["spf"],
        "authentication_dkim": scenario["dkim"],
        "authentication_dmarc": scenario["dmarc"],
        "spam_score": spam_score,
        "is_phishing": "true",
        "threat_level": (
            "High" if spam_score >= 0.9 else
            "Medium" if spam_score >= 0.7 else
            "Low"
        ),
        "mitre_technique": "T1566.001",
        "mitre_tactic": "Initial Access",
    }

    return event


def write_events(events, output_path):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
    print(f"[+] Wrote {len(events)} phishing event(s) to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Phishing Email Simulator for SOC Testing")
    parser.add_argument("--output", default="C:\\splunk_logs\\phishing\\phishing_emails.log")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument(
        "--scenario",
        choices=["credential_harvest", "invoice_fraud", "ceo_fraud", "malware_delivery", "all"],
        default="all",
    )
    parser.add_argument("--interval", type=float, default=0)
    parser.add_argument("--print-only", action="store_true")

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════╗
║     PHISHING EMAIL SIMULATOR - SOC LAB      ║
║     Scenario : {args.scenario:<28} ║
║     Count    : {args.count:<28} ║
║     Output   : {args.output[:28]:<28} ║
╚══════════════════════════════════════════════╝
""")

    events = []
    for i in range(args.count):
        event = generate_phishing_email(args.scenario if args.scenario != "all" else None)
        events.append(event)

        print(f"[{i+1}/{args.count}] [{event['threat_level']}] {event['scenario']}")
        print(f"    From      : {event['from']}")
        print(f"    To        : {event['to']}")
        print(f"    Subject   : {event['subject']}")
        print(f"    SpamScore : {event['spam_score']} | DKIM:{event['authentication_dkim']} SPF:{event['authentication_spf']}")
        print(f"    Attachment: {event['attachment_name']} ({event['attachment_size_bytes']} bytes)")
        print(f"    Hash      : {event['attachment_hash_sha256']}")
        print(f"    Malware   : {event['malware_family']} ({event['attachment_type']})")
        if event['has_link'] == 'true':
            print(f"    Link      : {event['link_url']}")
        print()

        if args.interval > 0 and i < args.count - 1:
            time.sleep(args.interval)

    if args.print_only:
        print("\n=== JSON OUTPUT ===")
        for e in events:
            print(json.dumps(e, indent=2))
    else:
        write_events(events, args.output)
        print(f"\n[✓] Done. Splunk search: index=main sourcetype=phishing-json")


if __name__ == "__main__":
    main()

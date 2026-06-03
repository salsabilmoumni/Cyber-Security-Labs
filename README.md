# 🔐 Cyber Security Labs
Hands-on cybersecurity projects covering SIEM engineering, SOC automation, cloud incident response, and malware analysis.  
Each lab is fully documented with tools, commands, configurations, findings, and MITRE ATT&CK mappings.

---

## 🗂️ Projects

| Project | Focus | Tools | Difficulty |
|---------|-------|-------|------------|
| [Automated SOC Pipeline](./Automation-SOC/) | End-to-end SOC automation — threat detection, IOC enrichment, case management, and one-click remediation | pfSense, Splunk, n8n, TheHive, VirusTotal API, Slack, Flask, Impacket, Hydra | Advanced |
| [AI-Powered SOC Pipeline — Splunk · Gemini · DFIR-IRIS](./AI-Powered-SOC-Automation/) | Fully automated Tier 1 SOC pipeline — MITRE ATT&CK detection via Atomic Red Team, AI triage with Google Gemini, VirusTotal hash enrichment, Slack alerting, and automatic DFIR-IRIS case creation | Splunk, Sysmon, Atomic Red Team, n8n, Google Gemini, VirusTotal, DFIR-IRIS, Slack | Advanced |
| [Sigma-YARA-SOC-Automation-Pipeline](./Sigma-YARA-SOC-Automation-Pipeline/) | Fully automated SOC triage pipeline — suspicious `.exe` detection via Sysmon, YARA file scanning, SigmaHQ rule fetch, AI-generated SPL hunt queries, VirusTotal IOC enrichment, and automatic incident creation in Jira + IRIS DFIR | n8n, Splunk, Sysmon, YARA, SigmaHQ, OpenAI GPT-4, VirusTotal, IRIS DFIR, Jira | Advanced |
| [Phishing-Email-Triage-Pipeline](./Phishing-Email-Triage-Pipeline/) | Fully automated phishing triage — Sysmon telemetry, Splunk detection, multi-IOC enrichment (IP, domain, URL, file hash), AI-powered Tier 1 analysis, and automatic case + ticket creation in DFIR-IRIS and Jira | Splunk, Sysmon, n8n, OpenAI GPT-4.1-mini, AbuseIPDB, VirusTotal, URLscan.io, DFIR-IRIS, Jira | Advanced |
| [SOC Automation — Splunk · TheHive · SOAR](./SOC-Automation-with-Splunk-TheHive-SOAR/) | Cloud SOC lab — endpoint telemetry, credential dumping detection, automated hash enrichment, case creation and analyst notification | Splunk, Sysmon, Shuffle, VirusTotal, TheHive | Intermediate |
| [Automated Active Directory Response](./Automated-Active-Directory-Response/) | Unauthorized RDP detection with automated analyst approval flow and Active Directory account disabling via LDAP | Splunk, Shuffle, Flask, ldap3, Active Directory, Slack, Vultr | Intermediate |
| [Elastic SIEM Home Lab](./elastic-siem/) | Log collection, threat simulation, custom alerting | Elastic Stack, Kali Linux, Nmap, KQL | Beginner |
| [Automated Phishing Detection](./phishing-detection/) | AI-powered email triage pipeline | Splunk, n8n, ChatGPT API, Slack | Intermediate |
| [AWS Incident Response](./aws-incident-response/) | Cloud IR — CloudTrail analysis, IAM investigation | AWS CLI, jq, CloudTrail | Intermediate |
| [Malware Analysis Lab](./malware-analysis/) | Static analysis of a real trojan sample | FLARE VM, PeStudio, CFF Explorer, HxD, VirusTotal | Intermediate |

---

## 🛠️ Skills Demonstrated

- **SOC automation & orchestration** — Shuffle/n8n workflows, Splunk webhook alerts, multi-branch incident pipelines
- **AI-assisted threat analysis** — OpenAI GPT-4 and Google Gemini as Tier 1 SOC analysts, AI-generated SPL hunt queries, structured triage verdicts, automated escalation decisions
- **Phishing detection & IOC enrichment** — Multi-vector IOC extraction (IP, domain, URL, file hash), AbuseIPDB reputation checks, URLscan.io analysis, VirusTotal enrichment, MITRE ATT&CK-mapped AI triage reports
- **YARA & Sigma rule-based detection** — File scanning against custom YARA signatures, SigmaHQ community rule fetching and SPL conversion
- **Firewall & network segmentation** — pfSense interface configuration, firewall rules, VPC design
- **SIEM deployment and detection engineering** — Elastic Stack, Splunk SPL, KQL, custom saved searches
- **Threat intelligence enrichment** — VirusTotal API v3, IOC classification, TheHive observables, SHA256 hash reputation
- **Active Directory attack simulation & detection** — Kerberoasting (T1558.003), RDP brute force (T1110.001), Event ID analysis, automated LDAP-based account remediation
- **Automated incident response** — Flask remediation API, LDAP account disabling, human-in-the-loop analyst approval via email
- **Cloud incident response** — CloudTrail log analysis, IAM investigation (AWS)
- **Windows malware static analysis** — PE structure, imports, strings, sandbox evasion indicators
- **MITRE ATT&CK mapping** across all labs

---

## 📁 Structure

```
Cyber-Security-Labs/
├── Automation-SOC/
│   ├── README.md
│   └── screenshots/
├── AI-Powered-SOC-Automation/
│   ├── README.md
│   └── screenshots/
├── Sigma-Yara-SOC-Automation-Pipeline/
│   ├── README.md
│   └── screenshots/
├── phishing-email-triage/
│   ├── README.md
│   ├── phishing_simulator.py
│   └── screenshots/
├── SOC-Automation-with-Splunk-TheHive-SOAR/
│   ├── README.md
│   └── screenshots/
├── Automated-Active-Directory-Response/
│   ├── README.md
│   ├── ldap_api/
│   │   └── ldap_api.py
│   └── screenshots/
├── elastic-siem/
│   ├── README.md
│   └── screenshots/
├── phishing-detection/
│   ├── README.md
│   └── screenshots/
├── aws-incident-response/
│   ├── README.md
│   └── screenshots/
└── malware-analysis/
    ├── README.md
    └── screenshots/
```

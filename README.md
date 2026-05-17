# 🔐 Cyber Security Labs

Hands-on cybersecurity projects covering SIEM engineering, SOC automation, cloud incident response, and malware analysis.  
Each lab is fully documented with tools, commands, configurations, findings, and MITRE ATT&CK mappings.

---

## 🗂️ Projects

| Project | Focus | Tools | Difficulty |
|---------|-------|-------|------------|
| [Automated SOC Pipeline](./Automation-SOC/) | End-to-end SOC automation — threat detection, IOC enrichment, case management, and one-click remediation | pfSense, Splunk, n8n, TheHive, VirusTotal API, Slack, Flask, Impacket, Hydra | Advanced |
| [Elastic SIEM Home Lab](./elastic-siem/) | Log collection, threat simulation, custom alerting | Elastic Stack, Kali Linux, Nmap, KQL | Beginner |
| [Automated Phishing Detection](./phishing-detection/) | AI-powered email triage pipeline | Splunk, n8n, ChatGPT API, Slack | Intermediate |
| [AWS Incident Response](./aws-incident-response/) | Cloud IR — CloudTrail analysis, IAM investigation | AWS CLI, jq, CloudTrail | Intermediate |
| [Malware Analysis Lab](./malware-analysis/) | Static analysis of a real trojan sample | FLARE VM, PeStudio, CFF Explorer, HxD, VirusTotal | Intermediate |

---

## 🛠️ Skills Demonstrated

- **SOC automation & orchestration** — n8n workflows, Splunk webhook alerts, multi-branch incident pipelines
- **Firewall & network segmentation** — pfSense interface configuration, firewall rules, VPC design
- **SIEM deployment and detection engineering** — Elastic Stack, Splunk SPL, KQL, custom saved searches
- **Threat intelligence enrichment** — VirusTotal API v3, IOC classification, TheHive observables
- **Active Directory attack simulation & detection** — Kerberoasting (T1558.003), RDP brute force (T1110.001), Event ID analysis
- **Automated incident response** — Flask remediation API, PowerShell AD actions triggered from Slack
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

---

<p align="center">Built by <a href="https://github.com/salsabilmoumni">salsabilmoumni</a></p>

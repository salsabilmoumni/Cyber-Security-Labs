# Cyber Security Labs

Hands-on cybersecurity projects covering SIEM engineering, cloud incident response, malware analysis, and SOC automation. Each lab is fully documented with tools, commands, findings, and MITRE ATT&CK mappings.

---

## Projects

| Project | Focus | Tools | Difficulty |
|---|---|---|---|
| [Elastic SIEM Home Lab](./elastic-siem/) | Log collection, threat simulation, custom alerting | Elastic Stack, Kali Linux, Nmap, KQL | Beginner |
| [Automated Phishing Detection](./phishing-detection/) | AI-powered email triage pipeline | Splunk, n8n, ChatGPT API, Slack | Intermediate |
| [AWS Incident Response](./aws-incident-response/) | Cloud IR — CloudTrail analysis, IAM investigation | AWS CLI, jq, CloudTrail | Intermediate |
| [Malware Analysis Lab](./malware-analysis/) | Static analysis of a real trojan sample | FLARE VM, PeStudio, CFF Explorer, HxD, VirusTotal | Intermediate |

---

## Skills demonstrated

- SIEM deployment and tuning (Elastic Stack)
- SOC automation and alert orchestration (n8n, Splunk webhooks)
- Cloud incident response and CloudTrail log analysis (AWS)
- Windows malware static analysis 
- Detection rule writing (KQL, Splunk SPL)
- MITRE ATT&CK mapping across all labs

---

## Structure

```
Cyber-Security-Labs/
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


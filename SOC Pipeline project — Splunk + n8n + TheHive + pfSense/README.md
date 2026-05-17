<img width="907" height="463" alt="image" src="https://github.com/user-attachments/assets/aaba85c6-a627-4e94-b038-39c4a106d701" /><img width="873" height="475" alt="image" src="https://github.com/user-attachments/assets/5edbca39-70da-4ab2-bcb3-1805f314e7b3" /># 🛡️ Automated SOC Pipeline — pfSense + Splunk + n8n + TheHive

> A fully automated Security Operations Center (SOC) pipeline built entirely on open-source tools. Threats are detected by Splunk, enriched via VirusTotal, triaged in TheHive, and analysts are notified — and can take remediation action — directly from Slack.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Stack](#-stack)
- [Network Layout](#-network-layout)
- [Phase 1 — Installation & Configuration](#phase-1--installation--configuration)
  - [pfSense Setup](#1-pfsense-setup)
  - [Sysmon](#2-sysmon)
  - [Splunk](#3-splunk)
  - [Active Directory](#4-active-directory)
  - [TheHive](#5-thehive)
  - [n8n](#6-n8n)
- [Phase 2 — Attack Simulations](#phase-2--attack-simulations)
- [Phase 3 — Detection & Alerting](#phase-3--detection--alerting)
  - [Attack 1 — Port Scan / Firewall Blocked Scanner](#attack-1--port-scan--firewall-blocked-scanner)
  - [Attack 2 — RDP Brute Force](#attack-2--rdp-brute-force)
  - [Attack 3 — Kerberoasting](#attack-3--kerberoasting)
- [Phase 4 — Incident Response & Remediation](#phase-4--incident-response--remediation)
- [Screenshots](#-screenshots)
- [References](#-references)

---

## 🔍 Overview

This project simulates a real-world SOC environment deployed on cloud infrastructure (Vultr). It covers the full detection-to-response lifecycle:

1. Attackers perform real attacks (port scan, RDP brute force, Kerberoasting)
2. Splunk detects anomalies and fires webhook alerts
3. n8n orchestrates the response: enriches IOCs via VirusTotal, opens cases in TheHive, and notifies analysts on Slack
4. Analysts can trigger one-click remediation (disable user / reset password) directly from Slack

---

## 🏗️ Architecture


> See [`screenshots/1.png`](screenshots/1.png) for the full architecture diagram.

---
---

## 🏗️ Full Workflow


> See [`screenshots/1.png`](screenshots/2.png) for the full workflow.

---
## 🧰 Stack

| Tool | Role | Port |
|------|------|------|
| **pfSense** | Firewall / network segmentation | — |
| **Splunk Enterprise** | SIEM — log ingestion, detection, alerts | 8000 |
| **n8n** | SOAR — workflow automation & orchestration | 5678 |
| **TheHive 5** | Case management platform | 9000 |
| **Slack** | Analyst notification & action channel | — |
| **VirusTotal API v3** | IOC enrichment (IP reputation) | — |
| **Impacket** | Kerberoasting simulation | — |
| **Hydra** | RDP brute force simulation | — |
| **Flask** | Remediation API on the AD server | 5000 |
| **Sysmon v15.2** | Windows endpoint telemetry | — |

---

## 🌐 Network Layout

| Interface | NIC | IP | Hosts |
|-----------|-----|----|-------|
| WAN | vtnet0 | 95.179.244.27 | Internet |
| ATTACKER | vtnet2 | 10.10.10.3/24 | Kali Linux |
| SECURITY | vtnet3 | 10.10.30.4/24 | Splunk, TheHive, n8n |
| VICTIM | vtnet4 | 10.10.20.3/24 | Windows DC, C1, C2 |

Firewall rules allow traffic between all segments through pfSense (which acts as default gateway), so logs from every VM flow through the firewall.

---

## Phase 1 — Installation & Configuration

### 1. pfSense Setup

Deploy pfSense on Vultr and configure a private VPC. Reference guide used: *"PFsense setup on Vultr with private LAN — Jarrod's Tech"*.

**Create interfaces:**

| Interface | IP |
|-----------|-----|
| WAN | 95.179.244.27 (public) |
| ATTACKER | 10.10.10.3/24 |
| SECURITY | 10.10.30.4/24 |
| VICTIM | 10.10.20.3/24 |

**Firewall rules:** Add a pass-all rule on each interface (source = subnet, destination = any) so machines can communicate and pfSense can collect logs.

**Set pfSense as the default gateway** on all VMs so every connection is routed through the firewall.

> See [`screenshots/3.png`](screenshots/3.png), [`screenshots/4.png`](screenshots/4.png), <img width="457" height="806" alt="image" src="https://github.com/user-attachments/assets/0b47242f-46cc-4ceb-b4fc-f5a29c7f9a0f" />


Thes status of the interfaces are up 
> See [`screenshots/6.png`](screenshots/6.png) for the interfaces status.

---

### 2. Sysmon

Install **Sysmon v15.2** on all three Windows machines (DC + 2 clients).

**Download:** [Sysmon — Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)  
**Config:** [olafhartong/sysmon-modular — sysmonconfig.xml](https://github.com/olafhartong/sysmon-modular/blob/master/sysmonconfig.xml) (schema 4.90)

```powershell
# Install Sysmon with config
.\Sysmon64.exe -i .\sysmonconfig.xml

# Verify
Get-Service Sysmon64
Get-WinEvent -ListLog "Microsoft-Windows-Sysmon/Operational"
```

Sysmon captures: process creation, network connections, file operations, registry changes, and more.

> See [`screenshots/7.png`](screenshots/7.png), [`screenshots/8.png`](screenshots/8.png)

---

### 3. Splunk

**Install Splunk Enterprise** on the Security VM and start it:

```bash
/opt/splunk/bin/splunk start
# Web UI available at http://<SECURITY_IP>:8000
```
> See [`screenshots/9.png`](screenshots/9.png), [`screenshots/10.png`](screenshots/10.png)

**Splunk Universal Forwarder** — install on all 3 Windows machines.

Configure `inputs.conf` at:
```
C:\Program Files\SplunkUniversalForwarder\etc\system\local\inputs.conf
```

```ini
[WinEventLog://Microsoft-Windows-Sysmon/Operational]
index = soc
disabled = 0

[WinEventLog://Security]
index = soc
disabled = 0
```

> ⚠️ Common issue: the default `inputs.conf` gets copied to local. Replace it with the minimal clean version above, then restart:

```powershell
Restart-Service SplunkForwarder
```

**Windows Audit Policy** — enable on all machines:

```cmd
auditpol /set /subcategory:"Filtering Platform Connection" /success:enable /failure:enable
```

After configured the forwarder the splunk received the telemetries of the 3 victim machines

> See [`screenshots/11.png`](screenshots/11.png)

---

### 4. Active Directory

Install **Active Directory Domain Services** on the Windows Server VM (hostname: `Moumni-ADDC01`).

**Steps:**
1. Server Manager → Add Roles → Active Directory Domain Services
2. Promote to Domain Controller, create domain `Moumni.local`
3. On Windows-C1 and Windows-C2: set DNS to the DC's IP (`10.10.20.5`), then join the domain

```
System Properties → Computer Name → Change → Domain: Moumni
```

After confirming with credentials → "Welcome to the Moumni domain."

> See [`screenshots/12.png`](screenshots/12.png), [`screenshots/13.png`](screenshots/13.png), [`screenshots/14.png`](screenshots/14.png)

---

### 5. TheHive

Install **TheHive 5** using Docker:

```bash
docker pull strangebee/thehive:5
# or use docker-compose
docker-compose up -d
# Available at http://<SECURITY_IP>:9000
```

> See [`screenshots/15.png`](screenshots/15.png)

---

### 6. n8n

Install **n8n** using Docker Compose.

`docker-compose.yml`:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=10.10.30.5
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - N8N_SECURE_COOKIE=false
      - GENERIC_TIMEZONE=Africa/Tunis
    volumes:
      - ./n8n_data:/home/node/.n8n
```

```bash
docker-compose up -d
# Available at http://<SECURITY_IP>:5678
```

> See [`screenshots/16.png`](screenshots/16.png)

---

## Phase 2 — Attack Simulations

Three attack types are simulated:

| # | Attack | Tool | Source |
|---|--------|------|--------|
| 1 | Port Scan / Host Sweep | nmap / Kali | 10.10.10.x |
| 2 | RDP Brute Force | Hydra | 10.10.10.x |
| 3 | Kerberoasting | Impacket GetUserSPNs | 10.10.10.x |

> See [`screenshots/17.png`](screenshots/17.png)

Configure the n8n webhook to receive the splunk alert

> See [`screenshots/19.png`](screenshots/19.png)
---

## Phase 3 — Detection & Alerting

All three Splunk saved searches fire webhook POSTs to n8n. 
A **Switch node** routes alerts to the correct workflow branch based on `search_name`.

**Switch Rules:**

| Rule | Condition | Branch |
|------|-----------|--------|
| RDP Brute Force | `search_name` contains `RDP` | Slack + TheHive Case |
| External Threat | `search_name` contains `External Threat` | Full pipeline (VT + TheHive + Slack) |
| Kerberoasting | `search_name` contains `Kerberoasting` | Slack + TheHive + Enrichment + Remediation |

> See [`screenshots/21.png`](screenshots/21.png)
---

### Attack 1 — Port Scan / Firewall Blocked Scanner

Detects any IP performing a port scan or host sweep that pfSense blocks — covers both external internet scanners and internal Kali attacks.

**Splunk Detection Query (`soc` index, source `pfsense`):**

```spl
index=soc sourcetype=pfsense
| rex field=_raw "filterlog\[\d+\]: (?P<csv>.+)"
| eval fields=split(csv, ",")
| eval action=mvindex(fields, 6)
| eval direction=mvindex(fields, 7)
| eval proto=mvindex(fields, 16)
| eval src_ip=mvindex(fields, 18)
| eval dst_port=mvindex(fields, 21)
| where action="block" AND direction="in" AND proto="tcp"
| where NOT match(src_ip, "^10\.")
| where NOT match(src_ip, "^172\.")
| where NOT match(src_ip, "^192\.168\.")
| where dst_port IN ("22", "3389", "445", "1433", "3306")
| stats dc(dst_port) as ports_scanned, count as total_packets by src_ip
| where total_packets > 3
| sort -total_packets
| head 3
| eval list(src_ip) as top_attackers, sum(total_packets) as total_blocked_packets, count as unique_ips
```
> See [`screenshots/18.png`](screenshots/18.png)

Alert fires when blocked traffic exceeds threshold → POST to n8n webhook.

**n8n Workflow Logic:**

The workflow of the External Threat - Firewall Blocked Scanners

> See [`screenshots/20.png`](screenshots/20.png)


```
Webhook (POST)
  └── Switch (mode: Rules)
        ├── RDP Brute Force → Send Slack message + Create TheHive Case
        └── External Threat
              └── Extract Fields (JavaScript — parse IPs from top_attackers)
                    └── VirusTotal API (GET /api/v3/ip_addresses/{ip})
                          └── IF malicious > 0
                                ├── TRUE → Create TheHive Case
                                │         → Create Observable (IP as IOC)
                                │         → Slack Alert 🚨
                                └── FALSE → Stop (IP is clean)
```
**JavaScript Extraction Node**
Extracts IPs from Splunk webhook payload before enrichment
> See [`screenshots/22.png`](screenshots/22.png)

**VirusTotal Enrichment:**
- Endpoint: `GET https://www.virustotal.com/api/v3/ip_addresses/{ip}`
- Auth: `x-apikey` header
- Fields used: `last_analysis_stats.malicious`, `country`, `as_owner`

> See [`screenshots/23.png`](screenshots/23.png)

**IF Node**
To classify if the ip is malicous or not
> See [`screenshots/24.png`](screenshots/24.png)

**TheHive Case fields:**
- Title: `External Threat - {ip}`
- Severity: Medium
- Tags: `ExternalThreat`, `{country}`, `VT-Malicious`
- Observable: IP address (type: `ip`, TLP: Amber, IOC: true)
> See [`screenshots/25.png`](screenshots/25.png), [`screenshots/26.png`](screenshots/26.png)

**Slack alert format:**
```
🚨 *External Threat Detected*
*IP:* 194.59.206.2
*Search:* External Threat - Firewall Blocked Scanners
*Total Packets:* 5
*Unique IPs:* 1
*VirusTotal Verdict:*
- Malicious: 7 - Suspicious: 4
- AS Owner: netcup GmbH
- Country: DE
🔗 VT Link: https://www.virustotal.com/gui/ip-address/194.59.206.2
Automated with this n8n workflow
```

> See [`screenshots/27.png`](screenshots/27.png), [`screenshots/28.png`](screenshots/28.png)

---
**Add Observable (IOC) to TheHive**
> See [`screenshots/29.png`](screenshots/29.png), [`screenshots/30.png`](screenshots/30.png)


### Attack 2 — RDP Brute Force

**Simulation (from Kali):**

```bash
hydra -l administrator \
  -P /usr/share/seclists/Passwords/CommonCredentials/10k-most-common.txt \
  -t 4 rdp://10.10.20.4
```

**Splunk Detection Query:**

```spl
index=soc sourcetype=WinEventLog EventCode=3389 DestinationPort=3389
| bin _time span=1m
| stats count by _time, SourceIp, DestinationIp
| where count > 50
```

Fires alert when >50 RDP connection attempts are seen from a single source within 1 minute.

> See [`screenshots/31.png`](screenshots/31.png)

**n8n Workflow:**

```
Webhook (POST)
  └── Switch → RDP Brute Force branch
        ├── Send Slack message (immediate alert)
        └── Create TheHive Case
              Title: "RDP Brute Force - {SourceIp}"
              Severity: High
              Tags: RDP, BruteForce, T1110.001
              Description: Attacker IP, Target IP, Attempt count
```
> See [`screenshots/32.png`](screenshots/32.png)

**TheHive Case**

> See [`screenshots/33.png`](screenshots/33.png), [`screenshots/34.png`](screenshots/34.png)

**Slack notification format:**
```
🚨 [HIGH] RDP Brute Force Detected
Attacker IP: 10.10.10.4
Target IP: 10.10.20.4
Attempts: 76
Search: RDP Brute Force Detected
🔗 Splunk Link: http://...
Automated with this n8n workflow
```

> See [`screenshots/35.png`](screenshots/35.png) through [`screenshots/36.png`](screenshots/36.png)

---

### Attack 3 — Kerberoasting

#### Setup on DC (PowerShell)

```powershell
# Create a low-privilege domain user
New-ADUser -Name "joe doe" -SamAccountName "joedoe" `
  -AccountPassword (ConvertTo-SecureString "Password123" -AsPlainText -Force) `
  -Enabled $true

# Create vulnerable service account
New-ADUser -Name "svc_http" -SamAccountName "svc_http" `
  -AccountPassword (ConvertTo-SecureString "Service123!" -AsPlainText -Force) `
  -Enabled $true -PasswordNeverExpires $true

# Register SPN
setspn -A HTTP/webserver.Moumni.local svc_http

# Enable RC4 encryption (makes it vulnerable)
Set-ADUser svc_http -KerberosEncryptionType RC4

# Verify
setspn -L svc_http
```

#### Simulation (from Kali/Attacker)

```bash
# Install Impacket
git clone https://github.com/fortra/impacket.git
cd impacket
pip install . --break-system-packages

# Enumerate SPNs
python3 /usr/local/bin/GetUserSPNs.py Moumni.local/joedoe:Password123 -dc-ip 10.10.20.5

# Request TGS hashes
python3 /usr/local/bin/GetUserSPNs.py Moumni.local/joedoe:Password123 -dc-ip 10.10.20.5 -request

# Crack hash offline (e.g. with hashcat)
```

#### Splunk Detection Query

```spl
index=soc EventCode=4769
| where Ticket_Encryption_Type="0x17"
| where NOT like(Service_Name, "%$")
| where Service_Name!="krbtgt"
| table _time, Account_Name, Service_Name, Client_Address, Ticket_Encryption_Type
| sort -_time
```

- Monitors **Event ID 4769** (Kerberos Service Ticket Request)
- Triggers on **RC4 encryption (`0x17`)** — the primary Kerberoasting indicator
- Payload sent to n8n: `Account_Name`, `Service_Name`, `IpAddress`, `Ticket_Encryption_Type`, MITRE tag

#### n8n Workflow — Kerberoasting Branch

```
Webhook (POST)
  └── Switch → Kerberoasting branch
        ├── Send Slack message (immediate analyst alert)
        │     - User, Service Account, Source IP
        │     - Encryption Type, Severity: HIGH
        │     - MITRE ATT&CK: T1558.003
        │     - Splunk investigation link
        │     - Recommended actions
        │
        └── Create TheHive Case (immediate)
              Title: "Kerberoasting attempt Detected - {Account_Name}"
              Severity: High
              Tags: T1558.003
              TLP/PAP: Amber
              │
              └── Enrich with Splunk (last 24h activity for the account)
                    POST http://10.10.30.3:8089/services/search/jobs
                    Query: EventCodes 4768/4769/4624/4625/4720/4722/4724/4738
                    │
                    └── Edit Fields (JavaScript)
                          Computes:
                          - tgsCount, tgtCount
                          - logonSuccess, logonFailed
                          - accountCreated, passwordReset
                          - accountModified
                          - riskLevel (CRITICAL / HIGH / MEDIUM)
                          - criticalFlags[]
                          - enrichmentSummary (markdown)
                          │
                          └── Update TheHive Case (add enrichment to description)
                                │
                                └── HTTP Request → Slack API (action-required message)
                                      - Enriched data (TGS count, risk level)
                                      - 🚫 Click to Disable AD User  (link → Webhook2)
                                      - 🔑 Click to Reset Service Password (link → Webhook1)
```

**Slack action message format:**
```
🚨 Kerberoasting Detected — Action Required
User: joedoe@MOUMNI.LOCAL
Service Account: svc_http
TGS Requests: 15
Risk Level: CRITICAL

Remediation Actions:
🚫 Click to Disable AD User
🔑 Click to Reset Service Password
```

> See [`screenshots/24.png`](screenshots/24.png) through [`screenshots/31.png`](screenshots/31.png)

---

## Phase 4 — Incident Response & Remediation

### Flask Remediation API (on AD Server)

A lightweight Flask API running on the Windows DC enables n8n to execute PowerShell commands remotely via HTTP.

**Setup:**

```bash
pip install flask requests
python C:\ad_api.py
# Listens on 0.0.0.0:5000
```

**Endpoints:**

| Endpoint | Method | Action |
|----------|--------|--------|
| `/health` | GET | Health check |
| `/disable-user` | POST | Disable AD account via `Disable-ADAccount` |
| `/reset-password` | POST | Reset password via `Set-ADAccountPassword` |

**Security:**
- API key authentication (`X-API-Key` header)
- New passwords generated randomly (25 chars, mixed charset)
- New password sent to Slack `#alerts` channel after reset

**AD Actions:**
- **Disable:** sets `userAccountControl = 514` via `Disable-ADAccount`
- **Reset:** generates random password via `Set-ADAccountPassword`

### Remediation Pipeline in n8n

```
Webhook2 (GET /disable-user?username=X)
  └── Disable_User_Request (POST → Flask API /disable-user)
        └── Confirm_User_Disabled (Slack confirmation)

Webhook1 (GET /reset-password?username=X)
  └── Reset_Password (POST → Flask API /reset-password)
        └── Confirm_Reset_Password (Slack confirmation with new password)
```

Both webhooks are permanently published. The analyst simply **clicks a link in Slack** → browser opens → webhook fires → PowerShell executes on the AD server → Slack confirms.

**Confirmation messages:**
```
✅ User has been disabled in Active Directory
Automated with this n8n workflow

✅ Password for svc_http has been reset
New Password: eXe*6e%bxSM8DCaBzub937&9b
Delete this message after sharing with service owner
Automated with this n8n workflow
```


## 🔗 References

- [pfSense on Vultr with private LAN — Jarrod's Tech](https://jarrod.tech)
- [Sysmon v15.2 — Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)
- [sysmon-modular config — olafhartong](https://github.com/olafhartong/sysmon-modular)
- [Impacket — fortra](https://github.com/fortra/impacket)
- [VirusTotal API v3](https://developers.virustotal.com/reference/overview)
- [TheHive Project](https://thehive-project.org/)
- [n8n Documentation](https://docs.n8n.io/)
- [MITRE ATT&CK T1558.003 — Kerberoasting](https://attack.mitre.org/techniques/T1558/003/)
- [MITRE ATT&CK T1110.001 — Password Guessing](https://attack.mitre.org/techniques/T1110/001/)

---

# AWS Incident Response Lab

A hands-on cloud incident response exercise based on the [flaws2.cloud](http://flaws2.cloud) challenge. Acting as a security analyst with IAM access to a "Security" account, the objective was to assume a cross-account role, retrieve CloudTrail logs from S3, and analyze them using `jq` to reconstruct the attack timeline and identify misconfigurations.

**Tags:** `aws` `cloud-security` `incident-response` `cloudtrail` `iam` `jq` `blue-team` `dfir`

---

## Lab overview

| Item | Detail |
|---|---|
| Platform | flaws2.cloud (AWS-based IR challenge) |
| Source account | Security — `322079859186` |
| Target account | Target — `653711331788` |
| Log source | S3 bucket `flaws2-logs` (CloudTrail JSON) |
| Tools | AWS CLI, jq, gunzip |
| Goal | Identify compromised IAM user and attack misconfigurations |

---

## Environment

```
[Security Account 322079859186]          [Target Account 653711331788]
         │                                          │
    user: security          ─────assume role──▶   role: security
         │
    s3: flaws2-logs
```

![Lab environment diagram](screenshots/01-environment-diagram.png)

---

## Investigation steps

### Step 1 — Configure AWS profile

```bash
aws configure --profile havoc
# AWS Access Key ID: AKIAIUFNQ2WCOPTEITJQ
# AWS Secret Access Key: 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
# Default region: (leave blank)
```

> **Note:** These are lab-provided credentials from the flaws2.cloud challenge — not real credentials.

### Step 2 — Verify identity

```bash
aws --profile havoc sts get-caller-identity
```

```json
{
    "UserId": "AIDAJXZBU42TNFRNGBBFI",
    "Account": "322079859186",
    "Arn": "arn:aws:iam::322079859186:user/security"
}
```

![STS get-caller-identity output](screenshots/02-sts-identity.png)

Confirmed we are operating as the `security` IAM user in the Security account.

### Step 3 — List S3 buckets

```bash
aws --profile havoc s3api list-buckets
```

```json
{
    "Buckets": [
        {
            "Name": "flaws2-logs",
            "CreationDate": "2018-11-19T20:54:31+00:00"
        }
    ],
    "Owner": {
        "DisplayName": "scott+flaws2_security",
        "ID": "0ff467deaf461e549934997a2df02d29c8010173b1464262782d522bce63bf46"
    }
}
```

![S3 bucket listing](screenshots/03-s3-list-buckets.png)

### Step 4 — Download CloudTrail logs

```bash
aws --profile havoc s3 sync s3://flaws2-logs ~/Desktop/
```

![S3 sync downloading CloudTrail files](screenshots/04-s3-sync.png)

Multiple compressed CloudTrail log files (`.json.gz`) were downloaded from the `us-east-1/2018/11/28/` path.

### Step 5 — Parse logs with jq

Navigate to the log directory and extract records:

```bash
ls
# 653711331788_CloudTrail_us-east-1_20181128T2235Z_cR9ra7OH1rytWyXY.json.gz
# ... (8 files total)

# Read all events using jq for formatted view
find . -type f -exec cat {} \; | jq '.'
```

![jq formatted CloudTrail output](screenshots/05-jq-output.png)

First notable event — an anonymous `GetObject` call at `23:09 UTC`:

```json
{
  "eventTime": "2018-11-28T23:09:36Z",
  "eventSource": "s3.amazonaws.com",
  "eventName": "GetObject",
  "userIdentity": {
    "type": "AWSAccount",
    "principalId": "",
    "accountId": "ANONYMOUS_PRINCIPAL"
  },
  "sourceIPAddress": "104.102.221.250",
  "requestParameters": {
    "bucketName": "the-end-962b72bjahfm5b4wcktm8t9z4sapemjb.flaws2.cloud",
    "key": "index.htm"
  }
}
```

### Step 6 — Extract event timeline

```bash
# List all event names
find . -type f -exec cat {} \; | jq '.Records[].eventName'

# Build a timeline with timestamps
find . -type f -exec cat {} \; | \
  jq -cr '.Records[][.eventTime, .eventName]|@tsv' | sort
```

![Sorted event timeline](screenshots/06-event-timeline.png)

---

## Attack timeline

| Time (UTC) | Event | Significance |
|---|---|---|
| 2018-11-28 22:31:59 | `AssumeRole` | Initial role assumption — attacker gains cross-account access |
| 2018-11-28 22:31:59 | `AssumeRole` | Second assume role call |
| 2018-11-28 23:02:56 | `GetObject` ×5 | Attacker begins reading S3 objects |
| 2018-11-28 23:03:08 | `GetObject` ×6 | Continued data access |
| 2018-11-28 23:03:12 | `AssumeRole` | Privilege escalation attempt |
| 2018-11-28 23:03:12 | `CreateLogStream` | Attacker creates log stream — potential cover tracks |

---

## Key findings

- A compromised IAM user successfully assumed a cross-account role (`arn:aws:iam::653711331788:role/level3`) due to an overly permissive trust policy.
- Anonymous access to an S3 bucket (`ANONYMOUS_PRINCIPAL`) was possible because the bucket lacked proper public access block settings.
- `GetObject` events dominated the timeline — indicating active data exfiltration or reconnaissance.
- `CreateLogStream` events suggest the attacker may have attempted to blend in with legitimate CloudWatch log activity.

---

## MITRE ATT&CK mapping

| Technique | ID |
|---|---|
| Valid Accounts: Cloud Accounts | T1078.004 |
| Exfiltration Over Web Service | T1567 |
| Use Alternate Authentication Material | T1550 |

---

## Tools used

| Tool | Purpose |
|---|---|
| AWS CLI | Profile configuration, S3 sync, STS identity |
| `jq` | Parsing and filtering CloudTrail JSON logs |
| `gunzip` | Decompressing `.json.gz` log files |
| `find` + `cat` | Combining multiple log files for bulk parsing |

---

## What I learned

- How cross-account IAM role assumption works and how it can be abused
- Using `jq` to filter CloudTrail logs by `eventName`, `userIdentity`, and `sourceIPAddress`
- Reconstructing an attack timeline from raw CloudTrail JSON
- What misconfigured S3 bucket policies and IAM trust policies look like in practice

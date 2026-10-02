## 🎯 What is BountyFlow?

**BountyFlow** is a semi-automated reconnaissance workflow designed for **bug bounty hunters and security researchers**.

Instead of manually running multiple reconnaissance tools, collecting their output, removing duplicates, and validating results one by one, BountyFlow connects the different stages into a single workflow.

The goal is simple:

> **Turn a target into a clean, actionable attack surface.**

BountyFlow is built around tools such as:

* 🔎 **SecurityTrails** — passive DNS & domain intelligence
* 🌐 **Subfinder** — subdomain discovery
* ⚡ **httpx** — HTTP service probing
* 🎯 **Takeover checks** — detection of potential subdomain takeover candidates

---

## 🧠 The Workflow

BountyFlow connects reconnaissance stages together:

```text
                    Target
                      │
                      ▼
             ┌────────────────┐
             │   Discovery    │
             └───────┬────────┘
                     │
             ┌───────▼────────┐
             │  Subdomain     │
             │  Enumeration   │
             └───────┬────────┘
                     │
                     ▼
             ┌────────────────┐
             │     Dedup      │
             └───────┬────────┘
                     │
                     ▼
             ┌────────────────┐
             │     httpx      │
             │ HTTP Probing   │
             └───────┬────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Live Hosts  Titles    Tech Stack
          │
          ▼
   ┌──────────────────┐
   │ Takeover Checks  │
   └────────┬─────────┘
            │
            ▼
     ┌──────────────┐
     │ Clean Output │
     └──────────────┘
```

---

## 🔎 Recon Pipeline

BountyFlow combines multiple sources to build a broader view of the target's external attack surface.

### 1. Passive Discovery

BountyFlow can use **SecurityTrails** and other passive sources to discover domain and DNS information.

This provides additional context beyond what a single subdomain enumeration source can return.

---

### 2. Subdomain Enumeration

Discovered domains are combined with results from **Subfinder**.

```text
example.com
     │
     ├── api.example.com
     ├── dev.example.com
     ├── staging.example.com
     ├── admin.example.com
     └── assets.example.com
```

Results are normalized and deduplicated before moving to the next stage.

---

### 3. HTTP Probing

BountyFlow feeds the discovered hosts into **httpx** to determine which endpoints are actually responding.

This allows the workflow to separate:

```text
Discovered
     ↓
Potentially reachable
     ↓
HTTP/HTTPS alive
```

Useful information such as HTTP status, title, technologies, and other probe metadata can then be collected.

---

### 4. Takeover Detection

Live and discovered subdomains can then be passed through takeover checks.

The goal is to identify domains that may be pointing toward external services with a potentially claimable or misconfigured resource.

```text
Subdomain
    ↓
DNS / HTTP information
    ↓
Service fingerprint
    ↓
Takeover check
    ↓
Potential candidate
```

Potential findings should always be manually verified before being reported.

---

## ⚡ Why BountyFlow?

A typical recon session can involve running several commands:

```text
Subfinder
    ↓
SecurityTrails
    ↓
Sort / Deduplicate
    ↓
httpx
    ↓
Takeover checks
    ↓
Filter results
    ↓
Start hunting
```

BountyFlow turns that repetitive setup into a reusable workflow.

Instead of spending your time moving output between tools, you can focus on the actual attack surface.


## 🧩 Built Around Proven Tools

BountyFlow acts as an orchestration layer around established reconnaissance tools.

| Tool                | Purpose                                |
| ------------------- | -------------------------------------- |
| **SecurityTrails**  | Passive DNS & domain intelligence      |
| **Subfinder**       | Subdomain enumeration                  |
| **httpx**           | HTTP probing & service discovery       |
| **Takeover** | Potential subdomain takeover detection |

This modular approach makes it easier to extend the workflow with additional reconnaissance tools in the future.

---

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/zanmu1337/BountyFlow.git
cd BountyFlow
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure the required reconnaissance tools are installed and available in your `$PATH`.

Configure your API keys and tool settings, then run BountyFlow against an authorized bug bounty target.

---

## 🗺️ The Philosophy

BountyFlow follows a simple recon philosophy:

```text
        DISCOVER
           ↓
        ENUMERATE
           ↓
         FILTER
           ↓
         VERIFY
           ↓
          HUNT
```

The workflow is **semi-automated by design**.

Automation handles the repetitive reconnaissance work.

The researcher makes the decisions.

---

## ⚠️ Disclaimer

BountyFlow is intended for **authorized security research, bug bounty programs, and penetration testing**.

Only use it against targets that are explicitly within the scope of a program or against systems you own or have permission to test.

Always respect the target's scope, rate limits, and program rules.

The author is not responsible for misuse, unauthorized scanning, or any damage caused by this tool.

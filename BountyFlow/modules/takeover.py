import re
import subprocess
import threading
import requests
 
DISCORD_WEBHOOK = "webhook_here"
 
FINGERPRINTS = [
    {"service": "AWS/Elastic Beanstalk", "status": "vulnerable", "cnames": ["elasticbeanstalk.com"], "nxdomain": True, "patterns": []},
    {"service": "AWS/S3", "status": "vulnerable", "cnames": ["s3.amazonaws.com", "s3-website"], "nxdomain": False, "patterns": [r"The specified bucket does not exist"]},
    {"service": "Agile CRM", "status": "vulnerable", "cnames": ["agilecrm.com"], "nxdomain": False, "patterns": [r"Sorry, this page is no longer available\."]},
    {"service": "Airee.ru", "status": "vulnerable", "cnames": ["airee.ru"], "nxdomain": False, "patterns": [r"Ошибка 402"]},
    {"service": "Anima", "status": "vulnerable", "cnames": ["animaapp.io"], "nxdomain": False, "patterns": [r"The page you were looking for does not exist\."]},
    {"service": "Bitbucket", "status": "vulnerable", "cnames": ["bitbucket.io"], "nxdomain": False, "patterns": [r"Repository not found"]},
    {"service": "Discourse", "status": "vulnerable", "cnames": ["trydiscourse.com"], "nxdomain": True, "patterns": []},
    {"service": "Gemfury", "status": "vulnerable", "cnames": ["furyns.com"], "nxdomain": False, "patterns": [r"404: This page could not be found\."]},
    {"service": "Ghost", "status": "vulnerable", "cnames": ["ghost.io"], "nxdomain": False, "patterns": [r"Site unavailable", r"Failed to resolve DNS path for this host"]},
    {"service": "HatenaBlog", "status": "vulnerable", "cnames": ["hatenablog.com"], "nxdomain": False, "patterns": [r"404 Blog is not found"]},
    {"service": "Help Juice", "status": "vulnerable", "cnames": ["helpjuice.com"], "nxdomain": False, "patterns": [r"We could not find what you're looking for\."]},
    {"service": "Help Scout", "status": "vulnerable", "cnames": ["helpscoutdocs.com"], "nxdomain": False, "patterns": [r"No settings were found for this company"]},
    {"service": "Helprace", "status": "vulnerable", "cnames": ["helprace.com"], "nxdomain": False, "patterns": []},
    {"service": "JetBrains", "status": "vulnerable", "cnames": ["youtrack.cloud"], "nxdomain": False, "patterns": [r"is not a registered InCloud YouTrack"]},
    {"service": "LaunchRock", "status": "vulnerable", "cnames": ["launchrock.com"], "nxdomain": False, "patterns": []},
    {"service": "Microsoft Azure", "status": "vulnerable", "cnames": ["cloudapp.net", "cloudapp.azure.com", "azurewebsites.net", "blob.core.windows.net", "azure-api.net", "azurehdinsight.net", "azureedge.net", "azurecontainer.io", "database.windows.net", "azuredatalakestore.net", "search.windows.net", "azurecr.io", "redis.cache.windows.net", "servicebus.windows.net", "visualstudio.com"], "nxdomain": True, "patterns": []},
    {"service": "Ngrok", "status": "vulnerable", "cnames": ["ngrok.io"], "nxdomain": False, "patterns": [r"Tunnel .*\.ngrok\.io not found"]},
    {"service": "Readme.io", "status": "vulnerable", "cnames": ["readme.io"], "nxdomain": False, "patterns": [r"The creators of this project are still working on making everything perfect!"]},
    {"service": "Strikingly", "status": "vulnerable", "cnames": ["s.strikinglydns.com", "strikinglydns.com"], "nxdomain": False, "patterns": [r"PAGE NOT FOUND\."]},
    {"service": "Surge.sh", "status": "vulnerable", "cnames": ["surge.sh"], "nxdomain": False, "patterns": [r"project not found"]},
    {"service": "SurveySparrow", "status": "vulnerable", "cnames": ["surveysparrow.com"], "nxdomain": False, "patterns": [r"Account not found\."]},
    {"service": "Uberflip", "status": "vulnerable", "cnames": ["read.uberflip.com", "uberflip.com"], "nxdomain": False, "patterns": [r"The URL you've accessed does not provide a hub\."]},
    {"service": "Wordpress", "status": "vulnerable", "cnames": ["wordpress.com"], "nxdomain": False, "patterns": [r"Do you want to register .*\.wordpress\.com\?"]},
    {"service": "Worksites", "status": "vulnerable", "cnames": ["worksites.net"], "nxdomain": False, "patterns": [r"Hello! Sorry, but the website you.{1,10}re looking for doesn.{1,10}t exist\."]},
    {"service": "Github", "status": "edge", "cnames": ["github.io"], "nxdomain": False, "patterns": [r"There isn['']t a GitHub Pages site here\."]},
    {"service": "Heroku", "status": "edge", "cnames": ["herokuapp.com", "herokudns.com"], "nxdomain": False, "patterns": [r"No such app"]},
    {"service": "Intercom", "status": "edge", "cnames": ["custom.intercom.help", "intercom.help"], "nxdomain": False, "patterns": [r"Uh oh\. That page doesn't exist\."]},
    {"service": "Netlify", "status": "edge", "cnames": ["netlify.app", "netlify.com"], "nxdomain": False, "patterns": [r"Not Found - Request ID:"]},
    {"service": "Shopify", "status": "edge", "cnames": ["myshopify.com"], "nxdomain": False, "patterns": [r"Sorry, this shop is currently unavailable\."]},
    {"service": "Tumblr", "status": "edge", "cnames": ["domains.tumblr.com"], "nxdomain": False, "patterns": [r"Whatever you were looking for doesn't currently exist at this address"]},
    {"service": "Vercel", "status": "edge", "cnames": ["vercel.com", "vercel-dns.com"], "nxdomain": False, "patterns": [r"DEPLOYMENT_NOT_FOUND"]},
    {"service": "Webflow", "status": "edge", "cnames": ["proxy.webflow.com", "proxy-ssl.webflow.com"], "nxdomain": False, "patterns": [r"The page you are looking for doesn't exist or has been moved\."]},
    {"service": "Wix", "status": "edge", "cnames": ["wixdns.net"], "nxdomain": False, "patterns": [r"Looks Like This Domain Isn't Connected To A Website Yet!"]},
]
 
print_lock = threading.Lock()
 
def safe_print(msg):
    with print_lock:
        print(msg, flush=True)
 
def send_discord(domain, status, services, cname, http_code, dns_status, matched_string):
    try:
        color = 0xff4444 if status == "confirmed" else 0xffaa00
        title = "CONFIRMED Subdomain Takeover" if status == "confirmed" else "SUSPICIOUS Subdomain Takeover"
 
        embed = {
            "title": title,
            "description": f"**Domain:** `{domain}`",
            "color": color,
            "fields": [
                {"name": "Service", "value": services, "inline": True},
                {"name": "DNS Status", "value": dns_status, "inline": True},
                {"name": "HTTP Code", "value": str(http_code) if http_code else "N/A", "inline": True},
                {"name": "CNAME", "value": f"```{cname}```" if cname != "-" else "No CNAME", "inline": False}
            ]
        }
 
        if matched_string:
            embed["fields"].append({"name": "Matched String", "value": f"```{matched_string[:200]}```", "inline": False})
 
        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]}, timeout=5)
    except:
        pass
 
def dig_cname(domain, server, timeout):
    try:
        result = subprocess.run(
            ["dig", f"@{server}", "+short", "+time=3", "+tries=2", "CNAME", domain],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return [], "dig_error"
        out = result.stdout.strip()
        if not out:
            return [], "no_cname"
        chain = [line.strip().rstrip(".").lower() for line in out.splitlines() if line.strip()]
        return chain, "ok"
    except subprocess.TimeoutExpired:
        return [], "timeout"
    except FileNotFoundError:
        return [], "dig_missing"
    except:
        return [], "error"
 
def dig_status(domain, server, timeout):
    try:
        result = subprocess.run(
            ["dig", f"@{server}", "+time=3", "+tries=2", "A", domain],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return "dig_error"
        m = re.search(r"status:\s*(\w+)", result.stdout)
        if m:
            return m.group(1).lower()
        return "unknown"
    except subprocess.TimeoutExpired:
        return "timeout"
    except FileNotFoundError:
        return "dig_missing"
    except:
        return "error"
 
def curl_fetch(url, timeout):
    try:
        if not url.startswith("http"):
            url = f"https://{url}"
        result = subprocess.run(
            ["curl", "-skL", "--compressed", "--max-time", str(timeout), "-o", "-",
             "-w", "\n---HTTPCODE:%{http_code}---", "-A",
             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
             url],
            capture_output=True, text=True, timeout=timeout + 5,
            errors="ignore"
        )
        out = result.stdout or ""
        m = re.search(r"---HTTPCODE:(\d+)---\s*$", out)
        if m:
            code = int(m.group(1))
            body = out[:m.start()]
        else:
            code = None
            body = out
        if code == 0:
            code = None
        return code, body
    except subprocess.TimeoutExpired:
        return None, ""
    except FileNotFoundError:
        return None, "CURL_MISSING"
    except:
        return None, ""
 
def get_matching_fingerprints(cname_chain):
    matches = []
    for fp in FINGERPRINTS:
        for cname in cname_chain:
            for sig in fp["cnames"]:
                if sig in cname:
                    matches.append(fp)
                    break
            if fp in matches:
                break
    return matches
 
def check_patterns(body, fingerprints):
    body = (body or "").replace("'", "'")
    matches = []
    for fp in fingerprints:
        for p in fp["patterns"]:
            m = re.search(p, body, re.IGNORECASE)
            if m:
                matches.append({"fp": fp, "matched_string": m.group(0)})
                break
    return matches
 
def analyze_matches(cname_chain, body):
    cname_fps = get_matching_fingerprints(cname_chain)
    pattern_matches = check_patterns(body, FINGERPRINTS)
 
    confirmed = []
    suspicious = []
 
    for fp in cname_fps:
        found_pattern = None
        for pm in pattern_matches:
            if pm["fp"] == fp:
                found_pattern = pm["matched_string"]
                break
 
        if found_pattern:
            confirmed.append({"fp": fp, "matched_string": found_pattern})
        else:
            suspicious.append({"fp": fp, "matched_string": None})
 
    for pm in pattern_matches:
        if pm["fp"] not in cname_fps:
            already_added = False
            for item in confirmed:
                if item["fp"] == pm["fp"]:
                    already_added = True
                    break
            if not already_added:
                suspicious.append(pm)
 
    return confirmed, suspicious
 
def check_domain(domain, dns_server, timeout, output_file):
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0]
    domain = domain.split(":")[0]
    
    if not domain or "." not in domain:
        return
    
    safe_print(f"[CHECK] {domain}")
 
    cname_chain, _ = dig_cname(domain, dns_server, timeout)
    dns_status = dig_status(domain, dns_server, timeout)
    
    safe_print(f"[DNS] {domain} | status={dns_status} | cname={' -> '.join(cname_chain) if cname_chain else 'none'}")
 
    http_code = None
    body = ""
 
    if dns_status != "nxdomain":
        for scheme in ("https", "http"):
            safe_print(f"[HTTP] Trying {scheme}://{domain}/")
            code, b = curl_fetch(f"{scheme}://{domain}/", timeout=3)
            if code is not None:
                http_code = code
                body = b
                safe_print(f"[HTTP] {domain} | {scheme} | code={code}")
                break
            elif b == "CURL_MISSING":
                break
 
    confirmed, suspicious = analyze_matches(cname_chain, body)
 
    if confirmed:
        services = ", ".join(f"{m['fp']['service']}" for m in confirmed)
        matched_strs = " | ".join(f"'{m['matched_string']}'" for m in confirmed if m['matched_string'])
        cname_plain = " -> ".join(cname_chain) if cname_chain else "-"
        
        threading.Thread(target=send_discord, args=(domain, "confirmed", services, cname_plain, http_code, dns_status, matched_strs), daemon=True).start()
        
        safe_print(f"[CONFIRMED] {domain} | dns={dns_status} | http={http_code} | cname={cname_plain} | match={services}")
        
        with open(output_file, 'a') as f:
            code = http_code if http_code is not None else "-"
            f.write(f"{domain}\t{dns_status}\t{code}\t{cname_plain}\t{services}\t{matched_strs}\n")
            f.flush()
    
    elif suspicious:
        services = ", ".join(f"{m['fp']['service']}" for m in suspicious)
        matched_strs = " | ".join(f"'{m['matched_string']}'" for m in suspicious if m['matched_string'])
        cname_plain = " -> ".join(cname_chain) if cname_chain else "-"
        
        threading.Thread(target=send_discord, args=(domain, "suspicious", services, cname_plain, http_code, dns_status, matched_strs if matched_strs else ""), daemon=True).start()
        
        safe_print(f"[SUSPICIOUS] {domain} | dns={dns_status} | http={http_code} | cname={cname_plain} | partial={services}")
    else:
        safe_print(f"[OK] {domain} | dns={dns_status} | http={http_code}")
 
def run_takeover(subdomains_file, output_file, dns_server="1.1.1.1", timeout=5, threads=10):
    try:
        with open(subdomains_file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        
        with open(output_file, 'w') as f:
            pass
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_domain, d, dns_server, timeout, output_file): d for d in domains}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    safe_print(f"error: {e}")
    
    except Exception as e:
        print(f"takeover error: {e}")
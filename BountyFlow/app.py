import sys
import os
from pathlib import Path
from modules.subfinder import run_subfinder
from modules.secu import run_securitytrails
from modules.httpx import run_httpx
from modules.takeover import run_takeover


def extract_domain(subdomain, base_domain):
    parts = subdomain.strip().split('.')
    base_parts = base_domain.strip().split('.')
    
    if len(parts) >= len(base_parts):
        if parts[-len(base_parts):] == base_parts:
            return subdomain.strip()
    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python app.py <domains_file>")
        sys.exit(1)
    
    domains_file = sys.argv[1]
    
    if not os.path.exists(domains_file):
        print(f"File not found: {domains_file}")
        sys.exit(1)
    
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]
    
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    

    results_file = output_dir / 'results.txt'
    
    all_subdomains = set()
    all_urls = set() 
    

    for domain in domains:
        print(f"[*] Collecting subdomains for {domain}")
        
        subs = run_subfinder(domain)
        for sub in subs:
            extracted = extract_domain(sub, domain)
            if extracted:
                all_subdomains.add(extracted)
        
        subs = run_securitytrails(domain)
        for sub in subs:
            extracted = extract_domain(sub, domain)
            if extracted:
                all_subdomains.add(extracted)
        
        print(f"[+] Total subdomains so far: {len(all_subdomains)}")
    

    if all_subdomains:
        print(f"[*] Running httpx on {len(all_subdomains)} subdomains")
        temp_input = output_dir / 'all_subdomains.txt'
        with open(temp_input, 'w') as f:
            for sub in sorted(all_subdomains):
                f.write(f"{sub}\n")
        
        run_httpx(sorted(all_subdomains), results_file)
    else:
        print("[!] No subdomains found")
        sys.exit(0)
    

    with open(results_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    

    if urls:
        print(f"[*] Running takeover scan on {len(urls)} URLs")
        run_takeover(str(temp_input), str(output_dir / 'takeover_results.txt'))
    

    if urls:
        print(f"[*] Running S3 scan on {len(urls)} URLs")
        run_s3_scan(str(results_file), str(output_dir / 's3_results.txt'))
    
    # Final: write only URLs to single file
    print(f"[+] Results saved to {results_file}")

if __name__ == "__main__":
    main()
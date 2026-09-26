import subprocess
 
def run_subfinder(domain):
    try:
        result = subprocess.run(
            ['subfinder', '-d', domain, '-silent'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        subdomains = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                subdomains.append(line)
        
        return subdomains
    except Exception as e:
        print(f"subfinder error for {domain}: {e}")
        return []
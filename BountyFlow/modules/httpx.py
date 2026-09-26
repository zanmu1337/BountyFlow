import subprocess
import os
import threading

def run_httpx(subdomains, output_file):
    if not subdomains:
        return

    status_codes = ['200', '301', '302', '403', '500']

    with open(output_file, 'w') as f:
        pass

    try:
        httpx_path = os.path.expanduser('~/go/bin/httpx')

        proc = subprocess.Popen(
            [httpx_path, '-silent', '-status-code', '-tech-detect', '-title', '-mc', ','.join(status_codes)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        def write_stdin():
            try:
                for sub in subdomains:
                    proc.stdin.write(f"{sub}\n")
                    proc.stdin.flush()
                proc.stdin.close()
            except:
                pass

        writer_thread = threading.Thread(target=write_stdin, daemon=True)
        writer_thread.start()

        with open(output_file, 'a') as f:
            for line in proc.stdout:
                line = line.strip()
                if line:
                    print(line)
                    url = line.split(' ')[0]
                    if url.startswith('http://') or url.startswith('https://'):
                        f.write(f"{url}\n")
                        f.flush()

        proc.wait(timeout=900)

    except Exception as e:
        print(f"httpx error: {e}")
# NetDump

NetDump summarizes network activity by method, HTTP status and media family. This public edition replaces provider-specific capture targets and settings with a generic Chrome DevTools listener and a small fictional HAR file. Routes, headers, query strings, cookies and response bodies are excluded from the output.

Run the offline example with Python 3.10 or newer.

```sh
python netdump.py --har example.har
```

For live observation, use a local disposable Chrome debugging profile, install `requirements.txt`, and select a page ID from the loopback debugger’s `/json/list`. Run `python netdump.py --tab PAGE_ID --port 9222 --seconds 10` while exercising that page. Each JSON row counts matching responses.

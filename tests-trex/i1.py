#!/root/venv/bin/python3.9
import asyncio
import asyncssh
import subprocess
import json
import re
from interface_diag import InterfaceDiagnostics
import time

# Usage Example:
async def main():
    hosts = {
            'sunset': ['redwest ']
            }

    diag = InterfaceDiagnostics(hosts=hosts)
    # print("Collecting start stats...")
    await diag.collect_data(phase="start")
    # print("\nCollecting end stats and computing differences...")
    # time.sleep(20)
    await diag.collect_data(phase="end")
    print("\nAll stats:\n")
    d = diag.export_stats_rooted()
    print(json.dumps(d, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

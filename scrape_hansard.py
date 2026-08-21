import json

with open("data.json", "w") as f:
    json.dump({"status": "ok"}, f)

with open("rss.xml", "w") as f:
    f.write("""<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Tas Hansard Test</title>
  </channel>
</rss>
""")

print("Files created")

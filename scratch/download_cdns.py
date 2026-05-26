import urllib.request
import os

static_dir = "/Users/ashishverma/Assignment1/HypnoFaux/static"
os.makedirs(static_dir, exist_ok=True)

urls = {
    "tailwind.js": "https://cdn.tailwindcss.com",
    "react.production.min.js": "https://unpkg.com/react@18.2.0/umd/react.production.min.js",
    "react-dom.production.min.js": "https://unpkg.com/react-dom@18.2.0/umd/react-dom.production.min.js",
    "lucide-react.min.js": "https://unpkg.com/lucide-react@0.344.0/dist/umd/lucide-react.min.js",
    "lucide.min.js": "https://unpkg.com/lucide@0.344.0/dist/umd/lucide.min.js"
}

for name, url in urls.items():
    dest = os.path.join(static_dir, name)
    print(f"Downloading {url} to {dest}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"Successfully downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name} from {url}: {e}")

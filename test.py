import os
import urllib.request
import urllib.error

OPENAI_API_URL = "https://api.openai.com/v1/models"


def main():
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENAI_API_KEY não encontrada no ambiente")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(OPENAI_API_URL, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            print("OK", resp.status)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print("ERRO", e.code, body)
    except Exception as e:
        print("ERRO", str(e))


if __name__ == "__main__":
    main()

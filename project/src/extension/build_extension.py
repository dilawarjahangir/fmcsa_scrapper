# src/extension/build_extension.py

import os
import tempfile
import zipfile

def create_proxy_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
    """
    Creates a temporary Chrome extension that sets up proxy authentication.
    """
    # Create a temporary directory for our extension files
    extension_dir = tempfile.mkdtemp()

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function(){{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    # Write manifest and background script to files
    manifest_path = os.path.join(extension_dir, "manifest.json")
    background_path = os.path.join(extension_dir, "background.js")

    with open(manifest_path, "w") as f:
        f.write(manifest_json)

    with open(background_path, "w") as f:
        f.write(background_js)

    # Optionally pack the extension into a zip archive if needed
    extension_zip_path = os.path.join(extension_dir, "proxy_auth_extension.zip")
    with zipfile.ZipFile(extension_zip_path, 'w') as zp:
        zp.write(manifest_path, arcname="manifest.json")
        zp.write(background_path, arcname="background.js")

    return extension_dir

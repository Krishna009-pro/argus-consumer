# ARGUS dashboard preview

This folder contains the React version of the ARGUS dashboard. It is useful for previewing the interface and walking through the product flow.

The page reads bundled report snapshots, and its company-intake steps use sample responses. It does not connect to the Python analysis engine, search the web, or fetch reports. Use the Streamlit app in the project root when you need live intake or current saved dossiers.

## Run it locally

Install Node.js, open a terminal in this folder, and run:

```powershell
npm ci
npm run dev
```

Vite prints a local address in the terminal. Open that address in your browser. To create a production build, run `npm run build`; generated build files are kept out of Git.

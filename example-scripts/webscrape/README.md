<div align="center">

<h1>Web Scrape Examples</h1>

<p>Fetch public web data or capture a webpage from a NightyScript command.</p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-NightyScript-3776AB?style=flat-square">
  <img alt="Node.js" src="https://img.shields.io/badge/Node.js-Puppeteer-339933?style=flat-square">
</p>

<p><a href="../../README.md"><strong>Back to the main documentation</strong></a></p>

</div>

---

| Example | Command | Dependency |
| --- | --- | --- |
| GitHub Trending Fetcher | `<p>trending` | `requests`, `beautifulsoup4` |
| Puppeteer Screenshot | `<p>puppshot <url>` | Node.js, `puppeteer` |

## GitHub Trending Fetcher

Fetch the names of GitHub's top trending repositories.

### Installation

```bash
pip install requests beautifulsoup4
```

### Usage

Load the script in NightyScript and run:

```text
<p>trending
```

## Puppeteer Screenshot

Use Node.js and Puppeteer to capture a webpage. The Python script contains the
JavaScript source and creates the runner at execution time.

### Installation

```bash
npm install puppeteer
```

### Usage

Load the script in NightyScript and run:

```text
<p>puppshot https://example.com
```

The command returns captured Node.js output after a screenshot error.

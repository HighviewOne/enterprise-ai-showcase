# 🏢 Enterprise AI Showcase

A [Streamlit](https://streamlit.io/) showcase and live-demo gallery for **58 AI-powered enterprise applications** built with [Claude](https://www.anthropic.com/claude).

## Overview

This is the landing page and demo hub for a portfolio of production-style enterprise AI apps spanning 13 industry categories — Healthcare, Finance, Education, Enterprise Ops, DevOps & SRE, Real Estate, Compliance & Risk, Productivity, Energy & Climate, GovTech, Insurance, Marketing & Sales, and Retail.

Each project pairs a Streamlit UI with a dedicated "engine" module that calls Claude to do the actual work — resume scoring, loan underwriting, compliance auditing, policy intelligence, mock interviews, and more.

## Features

- Browseable, category-color-coded catalog of all 58 applications
- Individual runnable demos under `pages/` (e.g. AI Resume Matcher, ROI Calculator, Loan Underwriting, Compliance Audit, Mock Interview Coach)
- Reusable Claude-backed logic in `engines/`
- Document parsing for PDF/DOCX inputs (`pdfplumber`, `python-docx`)

## Tech stack

- `streamlit` for the UI and multi-page navigation
- `anthropic` (Claude) for the AI engines
- `pandas` + `plotly` for data and charts
- `pdfplumber` / `python-docx` for document ingestion

## Project structure

```
app.py            # Landing page / catalog of all 58 apps
pages/            # Individual Streamlit demo apps
engines/          # Claude-backed logic for each app
examples/         # Sample inputs
.streamlit/       # Streamlit config
```

## Running locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # required for the AI engines
streamlit run app.py
```

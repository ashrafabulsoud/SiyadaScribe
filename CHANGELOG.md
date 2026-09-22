# Changelog

All notable changes to **SiyadaScribe** are documented in this file. See
[Conventional Commits](https://www.conventionalcommits.org) for commit
guidelines; releases are managed with
[release-please](https://github.com/googleapis/release-please).

## [2.4.2](https://github.com/ashrafabulsoud/SiyadaScribe/releases/tag/v2.4.2) (2026-09-22)

Resynced SiyadaScribe with upstream Phlox 2.4.2 (from 1.0.5). Highlights inherited from upstream:

* Multi-user authentication: username/password login, first-run admin setup, user management,
  per-user ownership of encounters, jobs, letters, templates, todos, settings and document collections.
* Audit log with retention settings and export.
* Localisation scaffolding (i18next), clinic language setting, multilingual speech-to-text.
* RAG rewritten on a pluggable vector store (sqlite-vec); ChromaDB removed. Existing RAG collections
  must be re-ingested.
* Patient demographics profiles, ambient-scribe consent, Wrap Up job extraction, PDF form filling,
  structured citations in chat.
* Frontend migrated to Chakra UI v3 / React 19 with TypeScript utilities and an SWR cache layer.
* Extensive security hardening (CSP, rate limiting, request size caps, PHI stripped from PubMed
  queries, admin-gated configuration endpoints).

### Changed

* Re-applied the SiyadaScribe branding across frontend, backend, desktop (Tauri) build, Flatpak
  packaging, Docker and CI.
* Environment variables `PHLOX_*` are now `SIYADASCRIBE_*`.

## [1.0.5](https://github.com/ashrafabulsoud/SiyadaScribe/releases/tag/v1.0.5) (2026-06-25)

Initial **SiyadaScribe** release.

### Changed

* Rebranded the application to SiyadaScribe across the web frontend, backend API, desktop (Tauri) build, Docker, CI workflows, and documentation.
* Repointed in-app repository and container-registry links to this repository.

SiyadaScribe is a self-hosted, privacy-focused clinical documentation tool with
AI-assisted transcription, note generation, and agentic tooling. It is a
rebranded distribution of an upstream MIT-licensed open-source project; the
original copyright notice is retained in [LICENSE](LICENSE).

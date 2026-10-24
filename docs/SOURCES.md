# Source manifest

Recorded 2026-09-16. This review is tied to these exact local PDF bytes, not an assumed latest online revision. Originals were read without modification. All 61 pages were text-extracted and read; selected central figures/tables were also visually reviewed.

Source IDs are stable across the notes, audit and plan. PDF page references are one-based. Short summaries and analysis are saved; full extracted paper text is not retained in the repository.

**Public-edition note:** local file paths were removed when this repository was published; the PDFs themselves are **not** redistributed. The SHA-256 values below identify the exact copies that were read, so a reader can verify their own copy if they have access to it.

## S: Shield summary

Secondary synthesis; no publication metadata assumed.

- Local source: `Shield.pdf` (local copy, not redistributed)
- Pages: 15
- Bytes: 707235
- SHA-256: `01f2a2d10ba8282aeb8440d6cf0d65a8601156d2b39304afb7fc658ff80d9f7a`

## D: Detecting rug pulls in decentralized exchanges: The rise of meme coins

Kalacheva et al. DOI: 10.1016/j.bcra.2025.100336. Online 12 July 2025; volume 7 (2026).

- Local source: `1.Detecting rug pulls in decentralized exchanges The rise of meme coins.pdf` (local copy, not redistributed)
- Pages: 13
- Bytes: 2370837
- SHA-256: `61830ee57e3e30ca8af119f93cd29f8b3fa039e9bbc64c1251f10ac889b96b47`

## C: Catching the Rug: Early Prediction of Fraudulent Memecoins on Solana via Machine Learning

Li et al. arXiv:2608.20271v1, 20 August 2026.

- Local source: `2.Catching the Rug Early Prediction of Fraudulent.pdf` (local copy, not redistributed)
- Pages: 9
- Bytes: 413794
- SHA-256: `e1a26bb9f543e9a9039713b6cf01da8bcc7dc3a6c1905a08dd9ef6ca2dd9adca`

## T: Trust Dynamics and Bot-Driven Responses: An Approach to Rug Pulls in Solana Meme Coin Markets

Li et al. WebSci 2025. DOI: 10.1145/3717867.3717922. PDF pp. 1-11 correspond to printed pp. 106-116.

- Local source: `3.Trust Dynamics and Bot-Driven Responses An Approach to Rug.pdf` (local copy, not redistributed)
- Pages: 11
- Bytes: 3921273
- SHA-256: `c48c2bf12d72f5c1a2b282d8a34e32e2c3c4f5335e36bde66347f2920037744d`

## M: MELT: A Behavioral Trace Dataset for High-Risk Memecoin Launch Detection

Hu et al. arXiv:2602.13480v2, 21 May 2026.

- Local source: `5. MELT ABehavioral Trace Dataset for High-Risk.pdf` (local copy, not redistributed)
- Pages: 13
- Bytes: 1605595
- SHA-256: `0aaabc15a24a9f6e7cfafca2d60e96629765d88c9e1de139c5ba9180c3a09e53`

## Scope and supplementary sources

- The separately mentioned paper 6 inside Shield.pdf was not among the requested primary papers. Its claimed rules remain unverified in this review. Other PDFs in the reviewer's local paper library were not included.
- Current protocol details were checked against [Solana authority documentation](https://solana.com/docs/tokens/basics/set-authority) and [Token Extensions](https://solana.com/docs/tokens/extensions) on 2026-09-16.
- The [authors' MELT repository](https://github.com/git-disl/MELT) README was inspected for dataset access and reproduction scope on 2026-09-16; implementation code and downloadable datasets were not audited or executed.
- At the time of the review, the project's own feature-engineering, data-fetching, gate-training and measurement modules were also inspected (those engine modules are not included in this research-only edition). Baseline commit of the full project: `030956a`.
- Poppler reported a compressed-stream warning while rendering the requested pages. The selected page images were produced and visually readable; the numerical corrections were checked against both extracted text and rendered tables.

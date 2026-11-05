# Three Flux Systems, Many Lessons

Slides and speaker notes for a 4-minute lightning talk at the WHOI technical lunch seminar. The talk covers lessons learned building three benthic flux systems in MACHINELab:

- **LECS**: Long-term Eddy Covariance System
- **GEMS**: Gradient Exchange Mass Spectrometry
- **EGCF**: Eel Grass Chamber Flux

Brett Longworth · Woods Hole Oceanographic Institution

## Viewing

The rendered slides are published by GitHub Actions to GitHub Pages:
<https://blongworth.github.io/flux-systems-lightning-talk/>

Every workflow run also uploads the rendered deck as a `slides` artifact on the Actions tab.

In the slides, press `S` for speaker notes (script and timing), `F` for fullscreen, and `Esc` for the slide overview.

## Building locally

Requires [Quarto](https://quarto.org) (CI uses 1.10.19).

```sh
quarto render          # output in _site/index.html
quarto preview talk.qmd
```

## Layout

| Path | Contents |
|---|---|
| `talk.qmd` | Slides and speaker notes |
| `whoi.scss` | revealjs theme based on the WHOI brand palette and widescreen template |
| `assets/` | WHOI template background images and logo |
| `images/` | System photos, plots, and funder logos (see `images/LOGO_SOURCES.md`) |
| `.github/workflows/publish.yml` | Renders on every push to `main` and deploys to Pages |

Photo and plot placeholders in `talk.qmd` each have a commented `swap in:` line with the image path and alt text, ready to uncomment.

## License

Text and code are licensed under [CC BY 4.0](LICENSE). The WHOI, Shell, NSF, and MassDEP logos and WHOI template imagery are trademarks or property of their owners and are not covered by this license.

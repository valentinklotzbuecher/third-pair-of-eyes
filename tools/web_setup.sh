#!/usr/bin/env bash
# Setup script for a Claude Code on the web environment that runs the DKF review skills.
#
# Paste this file's contents into the environment's settings (the environment menu in
# the session's title bar, then Edit, then Setup script). New sessions run it before
# Claude starts. It installs what a review needs that the cloud image lacks:
#
#   - R from Ubuntu's packages, with knitr and rmarkdown (Quarto's R engine needs both)
#   - Quarto, for rendering the product
#   - Poppler's PDF tools, if missing
#   - mistune, for the review form's HTML
#
# A product's own R packages are not installed here: the review installs what the
# product loads, or add them below as Ubuntu packages (r-cran-<name>, lower case).
#
# It can run again without changing anything. On failure it names the step and exits
# non-zero. The network access level must allow package managers and github.com.

set -euo pipefail

QUARTO_VERSION="1.10.19"
R_PACKAGES="r-base-core r-base-dev r-cran-knitr r-cran-rmarkdown"
# Add the product's packages here, for example: R_PACKAGES="$R_PACKAGES r-cran-survival"

step() { printf '\n== %s\n' "$1"; CURRENT_STEP="$1"; }
trap 'echo "web_setup.sh failed at: ${CURRENT_STEP:-start} (exit $?)" >&2' ERR

if [ "$(id -u)" -eq 0 ]; then SUDO=""; else SUDO="sudo"; fi
export DEBIAN_FRONTEND=noninteractive

missing=""
for p in $R_PACKAGES poppler-utils; do
  dpkg-query -W -f='${Status}' "$p" 2>/dev/null | grep -q "install ok installed" || missing="$missing $p"
done

if [ -n "$missing" ]; then
  step "apt: installing$missing"
  $SUDO apt-get update -qq
  # shellcheck disable=SC2086
  $SUDO apt-get install -y -qq --no-install-recommends $missing >/dev/null
else
  step "apt: R, knitr, rmarkdown and Poppler already installed"
fi

if command -v quarto >/dev/null 2>&1 && [ "$(quarto --version)" = "$QUARTO_VERSION" ]; then
  step "quarto $QUARTO_VERSION already installed"
else
  step "quarto: installing $QUARTO_VERSION"
  tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/quarto.tar.gz" \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
  $SUDO mkdir -p /opt/quarto
  $SUDO tar -xzf "$tmp/quarto.tar.gz" -C /opt/quarto
  $SUDO ln -sf "/opt/quarto/quarto-${QUARTO_VERSION}/bin/quarto" /usr/local/bin/quarto
  rm -rf "$tmp"
fi

if python3 -c "import mistune" 2>/dev/null; then
  step "mistune already installed"
else
  step "python: installing mistune"
  python3 -m pip install --quiet --disable-pip-version-check --root-user-action=ignore mistune \
    || $SUDO apt-get install -y -qq --no-install-recommends python3-mistune >/dev/null
fi

step "check"
Rscript -e 'suppressPackageStartupMessages({library(knitr); library(rmarkdown)}); cat(R.version.string, "\n")'
echo "Quarto $(quarto --version)"
pdftotext -v 2>&1 | head -n 1
python3 -c "import mistune; print('mistune', mistune.__version__)"
echo "web_setup.sh: done"

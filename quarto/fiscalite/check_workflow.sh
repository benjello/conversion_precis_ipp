#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/benjello/projets/conversion_precis_ipp"
"$ROOT_DIR/quarto/check_workflow.sh" fiscalite chapters/indirecte/indirecte.qmd

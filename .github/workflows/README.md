# workflows

`ci.yml` runs `tools/verify_all.sh --pio` on pull requests and on pushes to `main` and `reorg/**`. It only **checks**; it deploys nothing. The website is published by GitHub's own Pages workflow, which this folder does not touch.

# GDMC 2023
Submission by Niels-NTG for the [2023 AI Settlement Generation Challenge](https://gendesignmc.engineering.nyu.edu/).

Also check out the [repo](https://github.com/Niels-NTG/gdmc2023) if you aren't there already for post-submission developments.

In this competition participants design and implement an algorithm that constructs a settlement in Minecraft. Submissions are judged on the aesthetics and narrative qualities of the output, on how functional the structure is from a gameplay perspective, and how well it adapts to any arbitrary Minecraft landscape.

## Field Lab Gamma γ
Field Lab Gamma is a mysterious scientific research station that suddenly just appeared into the world. Where did it come from? Who were the staff? What were they looking for and where have they gone to?

### Setup
This script works combined with the [HTTP Interface Forge mod](https://github.com/Niels-NTG/gdmc_http_interface/) for Minecraft 1.19.2. The generator itself is written for Python 3.10 and requires the packages listed in `requirements.txt`. Also don't forget to run `git submodule update --init` to install the `MCTS` and `gdpc` packages. Start the generator by running `main.py`, no CLI arguments required. The structures will be placed somewhere within build area, this can be set by setting the buidarea by running `/setbuiltarea fromX fromY fromZ toX toY toZ` in Minecraft itself before running the generator.

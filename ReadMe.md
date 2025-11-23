# AI Basketball Prediction
Docs 11-22-25 V1 (For questions or comments:  Stephen Witty switty@level500.com)

This project was created in collaboration with Marty Buchanan, whose insights helped shape the direction and design of the system.

### Project Overview:
The AI Basketball Prediction project is an exploration into using ChatGPT to predict the University of Arkansas Razorback men's and women's basketball team victories and point spreads.  The 2025 / 2026 season is the target for the analysis.  Frequently throughout the season, GPT is asked to predict the outcome of each Razorback basketball game via multiple individual game prompts.  The AI is asked to predict the winner of the game along with the point delta between the winner and the loser.  The point delta is averaged across the multiple prompt outcomes.  The data produced by the project can be used to study how the AI model changes predictions for later games throughout the season.  In later prediction runs, all previous 2025 / 2026 season games are also provided to the model via API.  These past games include both games that included the Razorbacks and the ones that do not.

Source code and model output are included in this repository for each game prediction run.




### Usage:

- The software is a Python3 script and runs in the usual manner
- The scripts have been tested on Ubuntu
- Place your own API key toward the top of the Python script
- Edit the program constants as needed at the top of the Python script

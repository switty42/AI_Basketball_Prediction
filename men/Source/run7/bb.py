# Testing AI's ability to determine basketball winners
# Author Stephen Witty switty@level500.com
#
# Original example code from rollbar.com - GPT example
# Base code from AI_Probe at level500.com
#
# V1 10-26-25 - Initial release / dev
# V2 11-22-25 - sleeping 2 seconds between AI calls to avoid rate limit when switched to GPT 5.1

from openai import OpenAI #OpenAi

import time
import sys
import os
import random
import csv
import re

# API key below
# OpenAI key
key = "XXXXXXXXX"

# AI model below
ai_model='gpt-5.1' #OpenAI model

###################### Constants ##########################################################
NUMBER_OF_COUNTS = 3                                 # Number of prompts per game to submit to the AI
AI_ERROR_LIMIT = 25                                  # Number of times to retry AI if errors occur
ANSWER_PROBLEM_LIMIT = 150                           # Number of times to retry AI if answer is not properly formed

####### Appends text to the end of a file ###########
def write_to_file(filename, text):
   try:
      with open(filename, 'a') as f:
         f.write(text)
   except Exception as e:
      print(f"An error occurred: {e}")
      sys.exit()

######### Check for yes or no count in string ###########
def has_one_Y_or_N(text):
    return (
        (text.count("{Y}") == 1 and "{N}" not in text) or
        (text.count("{N}") == 1 and "{Y}" not in text)
    )

###### Check for valid score ####
def has_one_valid_number(text):
   # Match [1] through [500]
   pattern = r"\[(?:[1-9]|[1-9]\d|[1-4]\d\d|500)\]"
   matches = re.findall(pattern, text)
   return len(matches) == 1

##### Return the score value between brackets
def find_score(text):
    match = re.search(r'\[(\d+)\]', text)
    if match:
        return int(match.group(1))
    return None

########### This function formats an output string ####################
def print_string(string):
   cnt = 0
   for char in string:
      if not (char == " " and cnt == 0):
         print(char, end = "")
         cnt = cnt + 1
      if (cnt > 115 and char == " "):
         print()
         cnt = 0
   print()
   sys.stdout.flush()

#### OpenAI ############## Function - Call AI #########################################
def call_ai(prompt_message):
   try:
      client = OpenAI(api_key=key)
      completion = client.chat.completions.create(model=ai_model, messages=[ {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt_message}])

   except Exception as e:
      return False, "", "WARNING:  System Error during AI call: " + str(e)

   return True, completion.choices[0].message.content, ""

###############  Start of main routine ##############################################################
with open('prompt.txt', 'r', encoding='utf-8') as file:
    prompt_txt = file.read()

print("Starting........V2")
print("Prompt:")
print_string(prompt_txt)
print("Model: " + ai_model)
print("------------------------\n\n")

game_date = []
location = []
team = []
score = []
result = []
cycle = 0
ai_errors = 0
retry_count = 0
answer_problems = 0

# Open and read the CSV file
with open('schedule.csv', 'r', newline='') as file:
   reader = csv.reader(file)
   for row in reader:
      if (len(row) != 3):
         print("Error in csv file")
         sys.exit();

      game_date.append(row[0])
      location.append(row[1])
      team.append(row[2])

print("Team game data")
print("---------------------")
for i in range(len(game_date)):
   print(game_date[i].ljust(9)+ " " + team[i].ljust(23)  + " " + location[i])

# Open and read past game data from file
with open('past_games.csv', 'r', encoding='utf-8') as file:
    past_games = file.read()

print("Past game data")
print("-------------------")
print(past_games)

start_time=time.time()

while cycle < len(game_date): # Main loop to run prompts

   count = 0
   win = 0
   loss = 0
   win_score = 0
   loss_score = 0

   while(count < NUMBER_OF_COUNTS): 
      success = False
      while (not success):
         if (ai_errors == AI_ERROR_LIMIT):
            print("ERROR, Max AI error retry count reached, exiting");
            sys.exit()

         if (answer_problems == ANSWER_PROBLEM_LIMIT):
            print("ERROR, Max answer problem limit retry count reached, exiting");
            sys.exit()

         time.sleep(3)
         prompt = prompt_txt + "Game Date: " + game_date[cycle] + "\n\r" + "Game Location: " + location[cycle] + "\n\r" + "Opponent: " + team[cycle] + "\n\r"

         prompt = prompt + "\n\rBelow find past game data to include in your analysis of which team will win the above game.\n\r"
         prompt = prompt + "The past game data is in the format of a csv data file that starts with header data.\n\r"
         prompt = prompt + "After the header data, each line represents a past game.\n\r\n\r" + past_games + "\n\r"

         print("\n---------- Team number: " + str(cycle) + " Team name: " + team[cycle] + " Count: " + str(count) + " AI Errors: " +  str(ai_errors) + " AI Answer problems: " + str(answer_problems) + "\n\r")
         print(prompt,flush=True)

         success, ai_reply, error_text = call_ai(prompt) # Call AI, retry if error

         if (not success):
            print(">>>>>> AI returned and error: " + error_text + "\r\n")
            ai_errors = ai_errors + 1
            continue

         print("---- AI Answer --------")
         print(ai_reply)

         if (has_one_Y_or_N(ai_reply) == False):
            print(">>>>> Answer error on Y / N")
            success = False
            answer_problems = answer_problems + 1
            continue

         if (has_one_valid_number(ai_reply) == False):
            print(">>>>> Answer error score")
            success = False
            answer_problems = answer_problems + 1
            continue

      game_score = find_score(ai_reply)
      if ("{Y}" in ai_reply):
         win = win + 1
         print("--- Single game win detected")
         win_score = win_score + game_score

      else:
         loss = loss + 1
         print("---- Single game loss detected")
         loss_score = loss_score + game_score

      print("Score found: " + str(game_score))
      count = count + 1

   print("######## Cumulative game result, wins: " + str(win) + " losses: " + str(loss) + " total lose score: " + str(loss_score) + " total win score: " + str(win_score))

   if (win > loss):
      result.append(True)
      print("Adding win to result list")
      avg=round(win_score / win)
      print("Add average win score: " + str(avg))
      score.append(avg)
   else:
      result.append(False)
      print("Adding loss to result list")
      avg=round(loss_score / loss)
      print("Add average loss score: " + str(avg))
      score.append(avg)

   cycle = cycle + 1

print("Run Complete")

print("\n------------------- Final report ----------------------")
print("AI Prompt:")
print_string(prompt_txt)
print("AI model: " + ai_model)

print("\nNumber of cycles per game: " + str(NUMBER_OF_COUNTS))
print("AI errors: " + str(ai_errors))
print("AI answer errors: " + str(answer_problems))
print("Run time in seconds: " + str(round(time.time() - start_time)))
print("\n\n---- Results -----------------------------------------------------")

for i in range(len(game_date)):
   print(game_date[i].ljust(9)+ " " + team[i].ljust(23)  + " " + location[i].ljust(20)[:20] + "  Score delta: " + str(score[i]).ljust(3),end="")
   if (result[i] == True):
      print(" Razorbacks win!!!!!")
   else:
      print(" Razorback lose")

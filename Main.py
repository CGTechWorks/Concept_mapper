import requests
import os
from datetime import datetime

#Configuration
LLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

#Logging config
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #Folder of this script
PROJECT_ROOT = os.path.dirname(BASE_DIR) #Front facing folder

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR) #Create folder if it doesn't exist

todays_date = datetime.now().strftime("%Y-%m-%d") #YYYY-MM-DD
LOG_FILE = os.path.join(LOG_DIR, f"model_responses_{todays_date}.log")

#Note: Full prompt has been removed for portfolio version
def call_model(user_prompt):
    fake_response= """
    BLOCK_TYPE=Decision
    CATEGORY=Concept breakdown
    QUESTION=What aspect should be explored first?
    1. First direction
    2. Second direction
    3. Third direction
    4. Fourth direction
    """

    return fake_response

#Log session builders + function
session_counter = 1
decision_path = []
decision_state = {} #Dictionary: Category > selected value
original_prompt = ""

def write_log(text):
    with open(LOG_FILE, "a") as f: #"a" = append mode
        f.write(text + "\n")

def response_parser(response_text):
    lines = response_text.split("\n")


    category = ""
    question = ""
    options = []
    block_started = False

    for line in lines:
        line = line.strip()

        if line.startswith("BLOCK_TYPE"):
            block_started = True
            continue

        if not block_started:
            continue

        if line.startswith("CATEGORY="):
            category = line.replace("CATEGORY=", "").strip()

        elif line.startswith("QUESTION="):
            question = line.replace("QUESTION=", "").strip()

        elif line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
            option_text = line.split(".", 1)[1].strip()
            options.append(option_text)

    return category, question, options[:4]

def normalize_category(category):
    return category.strip().upper().replace(" ", "_")

def should_end(decision_state, category):
    #Enough dimensions are resolved
    if len(decision_state) >= 6:
        return True
    
    #Category repetition signal (low value loop)
    if category == "FEATURE" and "FEATURE" in decision_state:
        return True
    
    return False

def build_final_output(decision_state, original_prompt):
    #Build a structured concept
    concept_lines = "\n".join(f"{k}: {v}" for k, v in decision_state.items())

    #Build simple name (let model improve later if needed)
    name_parts = list(decision_state.values())
    final_name = f"{" ".join(name_parts[:3])} {original_prompt.split()[-1]}" #Simple, readable label

    return f"""
    BLOCK_TYPE=End
    FINAL_NAME={final_name}

    FINAL_CONCEPT:
    {concept_lines}
    """

def build_final_name(decision_state):
    """
    Builds a descriptive FINAL_NAME from decision_state dictionary.
    decision_state = dict (CATEGORY > selected_option)
    """

    type_value = decision_state.get("TYPE", "")
    structure = decision_state.get("STRUCTURE", "")
    feature = decision_state.get("FEATURE", "")
    style = decision_state.get("STYLE", "")
    purpose = decision_state.get("PURPOSE", "")

    parts = []

    #STRUCTURE + TYPE (core object)
    if structure and type_value:
        parts.append(f"{structure.lower()} {type_value.lower()}")
    elif type_value:
        parts.append(type_value.lower())

    #FEATURE (key descriptor)
    if feature:
        parts.append(f"with {feature.lower()}")

    if style:
        parts.append(f"and {style.lower()} design")

    if purpose:
        parts.append(f"for {purpose.lower()}")
    
    clean_parts = []
    seen_parts = set()
    
    for part in parts:
        if part not in seen_parts:
            clean_parts.append(part)
            seen_parts.add(part)

    #Join everything
    final_name = " ".join(clean_parts)
    final_name = final_name.replace(" and and", "and")

    return final_name.capitalize()

#------

#Start loop - run ONCE for portfolio demonstration
for _ in range(1):
    #Initialize per session
    last_category = None
    reroll_flag = False
    reroll_options_flag = False

    user_input = input("\nEnter your concept, type 'exit' to exit program: ")

    if user_input.lower() == "exit":
        break

    #BEGIN LOGGING SESSION
    decision_path = [] #Reset path
    original_prompt = user_input #Store root concept

    session_id = f"{todays_date}_{session_counter:02d}" #Example: 2026-03-27_01
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Write session start
    write_log("="*50)
    write_log(f"SESSION_ID: {session_id}")
    write_log(f"START_TIME: {start_time}")
    write_log(f"USER_PROMPT: {original_prompt}")
    write_log(f"[STEP]")
    write_log("="*50 + "\n")

    state_lines = "\n".join(f"- {k}: {v}" for k, v in decision_state.items())

    reroll_instruction = ""
    reroll_options_instruction = ""
    

    if reroll_flag and last_category:
        reroll_instruction = f"""
        The previous CATEGORY was: {last_category}
        When rerolling:
        - You MUST choose a DIFFERENT CATEGORY if possible
        - If another valid conceptual dimension exists, do NOT repeat the same CATEGORY
        - Only reuse the same CATEGORY if no other meaningful dimension is available
        - Do NOT rephrase the same question
        """
    
    if reroll_options_flag and last_category:
        reroll_options_instruction = f"""
        The current CATEGORY is: {last_category}

        Previous OPTIONS were:
        {"\n".join(f"- {opt}" for opt in last_options)}

        When rerolling options:
        - Keep the SAME CATEGORY and QUESTION
        - Generate a NEW SET of OPTIONS
        - You MUST avoid repeating previous options
        - You MUST introduce meaningfully DIFFERENT alternatives
        - Do NOT reuse similar phrasing or synonyms of previous options
        - Expand the space of possible answers within this CATEGORY
        """

    current_prompt = f"""
    CONCEPT: {original_prompt}
    
    DECISIONS MADE:
    {state_lines}

    {reroll_instruction}
    {reroll_options_instruction}

    Generate the NEXT decision only.
    Do NOT repeat categories that are already resolved.
    """

    #DECISION LOOP
    for _ in range(1):
        result = call_model(current_prompt) #Pass user input to call model function

        print("\n---MODEL OUTPUT ---")
        print(f"BLOCK_TYPE=Decision")

        category, question, options = response_parser(result)
        reroll_flag = False
        reroll_options_flag = False
        category = normalize_category(category)
        last_category = category
        last_options = options
        

        if should_end(decision_state, category):
            #Ask model to finalize
            final_prompt = f"""
            CONCEPT: {original_prompt}

            DECISIONS MADE:
            {state_lines}
            
            Generate FINAL output.
            """
            final_output = call_model(final_prompt)

            print("\n ---FINAL RESULT ---")
            print("BLOCK_TYPE=End")

            final_name = build_final_name(decision_state)
            print(f"FINAL_NAME={final_name}")
            
            print(final_output)

            write_log("[END]")
            write_log(final_output)

            break

        if not category or len(category) > 25:
            print("Invalid category detected. Skipping step.")
            continue

        #Log step
        write_log("[STEP]")
        write_log(f"PATH: {original_prompt} {' -> '.join(decision_path) if decision_path else ''}")
        write_log("STATE:")
        for k, v in decision_state.items():
            write_log(f"{k}: {v}")
        write_log("RESPONSE:")
        write_log(result)
        write_log("-"*30 + "\n")

        if not options:
            print("No options returned. Ending session.")
            break

        #Show options to user
        print(f"\n{question}")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")

        choice = input("Select option number, type 'ro' = reroll options, 'm' = manual input, or 'done': ")

        #Ends program
        if choice.lower() == "done":
            break

        #Reroll entire category, question and options
        if choice.lower() == "r":
            print("\n---REROLLING DECISION---")            

            #Log reroll direction
            write_log("[REROLL]")
            write_log(f"PATH: {original_prompt} {' -> '.join(decision_path) if decision_path else ''}")
            write_log(f"LAST_CATEGORY: {last_category}")
            write_log("-"*30 + "\n")

            #Tracks rerolls
            reroll_flag = True
            reroll_options_flag = False
            continue

        #Reroll options only
        if choice.lower() == "ro":
            print("\n---REROLLING OPTIONS---")

            write_log("[REROLL OPTIONS]")
            write_log(f"PATH: {original_prompt} {' -> '.join(decision_path) if decision_path else ''}")
            write_log(f"CATEGORY: {last_category}")
            write_log("-"*30 + "\n")

            reroll_options_flag = True
            continue
        
        #Manual response flag
        is_manual = False

        #Allows manual response
        if choice.lower() == "m":
            user_value = input ("Enter your custom value: ").strip()

            if not user_value:
                print("Invalid input. Try again.")
                continue

            selected_option = user_value
            is_manual = True

            print(f"\n[MANUAL INPUT ACCEPTED] > {selected_option}")
        
        else:
            if not choice.isdigit() or int(choice) < 1 or int (choice) > len(options):
                print("Invalid choice. Try again.")
                continue

            selected_option = options[int(choice)-1]
            is_manual = False

        #Update decision path
        decision_path.append(selected_option)

        #Store category > value
        category = normalize_category(category)
        decision_state[category] = selected_option

        #Log manual input correctly vs normal selection
        if is_manual:
            write_log(f"[MANUAL_INPUT] {category}: {selected_option}")
        else:
            write_log(f"[SELECTION] {category}: {selected_option}")

        #Build next prompt (NEW SPINE)
        state_lines = "\n".join(f"- {k}: {v}" for k, v in decision_state.items())
        current_prompt = f"""
        CONCEPT: {original_prompt}

        DECISIONS MADE:
        {state_lines}

        Generate the NEXT decision only.
        Do NOT repeat categories that are already resolved.
        """


    #END LOG SESSION
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    write_log("="*50)
    write_log("END_SESSION")
    write_log(f"END_TIME: {end_time}")
    write_log("="*50 + "\n\n")

    session_counter += 1
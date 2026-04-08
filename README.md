Concept Mapper (Prototype)

## What
This is a local, AI-inspired (originally built using qwen2.5:7b model for prototype) exploration engine designed to break vague ideas into structured decision paths.

This system simulates a guided thinking process by:
- Generating conceptual categories
- Asking structured questions
- Presenting multiple directions with the options to manually input an option, or reroll the options
- Building decision paths over time


## Why
I built this because I wanted to take an abstract concept, and use AI as a tool to break down the concept to the core components, allowing someone to see the structure of their "train of thought". This helps the user think in a straight line, rather than thinking in circles. While most tools jump to straight answers, this focuses on structured exploration of a concept.


## How
- A vague concept is provided by the user: "Bake a cake, build a robot, design a car, design a website"
- The system generates a "decision block" (category + question + options)
- The user selects an option, manually injects their own, or rerolls the options (disabled in portfolio version).
- The system updates the state, and continues exploration

## Architecture components
- Response parsing system (structured text becomes usable data)
- Decision state tracking (Category stores selected value)
- Iterative decision loop
- Logging system for session tracking


## How do I run it? What are the requirements?
>>python main.py
(If that doesn't work, try 'python3 main.py')

- Python 3.x

Standard library modules used:
-os
-datetime

No external dependencies should be required for this version.


## Notes (Important)
- This is a portfolio-safe version
- Full backend prompt logic has been intentionally removed
- Model calls have been replaced with a simulated response
- Screenshots may show the current working version using a local AI model (qwen2.5:7b)

This repository focuses on:
- System design
- Flow control
- Parsing structured outputs

It does not focus on model performance, or final output quality.


## What can't it do right now?
- This uses a static response instead of a live model
- Reroll logic is partially disabled in this version
- Output is simplified for demonstration


## What's in store for this project?
- This project is part of a larger system that is intended to evolve into:
Concept > structured understanding > procedural execution

The execution layer is not included.

Author:
CGTechWorks


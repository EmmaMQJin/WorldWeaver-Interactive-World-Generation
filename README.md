# WorldWeaver-Interactive-World-Generation
### Notes on Map (Location + Connections) Generation


### Human-in-the-loop
- Initially, the user would be prompted for a description of the type of game they would like to build (can be anything)
- If their description is long or complicated, summarize for prompting later models
- After that, user is prompted to either start with generating locations or characters
- Once both are done, the user is prompted for generating objects
- Ideally, would take user input and feedback for each generation
- Note: we should write to external json file in each step

1. prompt for user input (read from file for now)
2. what do you want to start with? locations / characters
3. if user chooses to start with locations:
do you have any thoughts on the central location of the game?
if user inputs sth, incorporate that with initial story description for 
generating the central location
4. Generate neighboring locations (for now, just write generated neighboring locations to file)
and let user edit file (ideally, should define what the user can edit and render on webpage)
5. Go as many rounds of neighboring location generations as the user wants
6. For characters, generate main character first, and then NPCs
7. For Objects, generate the object based on user input (if any); let the user choose who to give it to / where to put it
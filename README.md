GateKeeper: Password Manager ‎‎

1.) Project Overview:

Our app GateKeeper, ensures your passwords are organized, kept, and protected. Other than that, this app contains a built-in password strength checker. Incase of any circumstances that may occur, you have a password checker ready and saved passwords organized and ready. Ensuring trust, liability, and security.

2.) Updated Feature List
   
  1. Account Storage System
    - GateKeeper lets users save different accounts with their app name, category, and password in one place.
  2. Built-in Password Strength Checker
    - The app checks how strong a password is and tells the user how to make it better.
  3. Account Categorization
    - Users can organize their accounts into groups like Academic, Personal, or Internship.
  4. Secure Local Data Handling
    - All account information is saved on the user’s device and is not sent online.

3.) Technologies Used (With Justification)
  - Python – Main programming language used to build the system logic.
  - JSON – Used to store account data in a structured and readable format.
  - Regular Expressions (re module) – Used for password validation and strength checking.
  - Git – Version control system used to track project changes.
  - GitHub – Repository hosting and collaboration platform.
  - Visual Studio Code – Development environment used to write and manage code.

4.) Detailed Methodology:

  - How Core Features Were Implemented
  The password keeper was implemented using Python functions that allow users to input account information and store it in a JSON file.
  The password strength checker uses conditional logic and regex patterns to analyze password complexity and return improvement suggestions.
  
  - Key Design Decisions
    1. Chose JSON for simplicity and readability.
    2. Focused on command-line interface before adding graphics.
    3. Expanded scope from password checker to full password keeper system.

  - Trade-offs
    1. Did not implement encryption due to current skill level.
    2. Graphics and notifications postponed for future versions.
   
6.) Installation Instructions
Clone the repository:
git clone https://github.com/jzdispo2030-coder/CS_CLog-RMe.git

Navigate into the folder:
cd GateKeeper

Run the program:
python main.py

5.) Programming & Computing Ethics
  - This project considers ethical responsibilities in software development.
  - User privacy was considered by limiting stored data.
  - Open-source tools and technologies were properly credited.
  - Accessibility and simplicity were prioritized in design.
  - The project aligns with principles from the ACM Code of Ethics, particularly regarding privacy and responsible computing.
    
In developing GateKeeper, we considered important ethical responsibilities in programming. We respected intellectual property by writing our own
original code and properly crediting any tools or technologies used, such as Python and ChatGPT.

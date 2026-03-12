GateKeeper: Password Manager

I. Project Overview:

Our app GateKeeper ensures your passwords are organized, kept, and protected. Other than that, this app contains a built-in password strength checker. In case of any circumstances that may occur, you have a password checker ready and saved passwords organized and ready. Ensuring trust, liability, and security.

II. Feature List

  1. Account Storage System
     - GateKeeper lets users save different accounts with their app name, category, and password in one place.
  
  2. Built-in Password Strength Checker
     - The app checks how strong a password is and tells the user how to make it better.
  
  3. Account Categorization
     - Users can organize their accounts into groups like Academic, Personal, Internship, or Other.
  
  4. Secure Local Data Handling
     - All account information is saved on the user's device and is not sent online.
  
  5. Password Generator
     - Generate strong, random passwords with one click.
     - Ensures mix of uppercase, lowercase, numbers, and symbols.
  
  6. Password Reuse Detection
     - Automatically detects passwords used in multiple accounts.
     - Helps improve security by identifying risky practices.
  
  7. Graphical User Interface (GUI)
     - Visual account management with point-and-click interface.
     - Real-time search as you type.
     - One-click password copy to clipboard.
     - Show/hide password toggle.
     - Visual password strength meter.
     - Color-coded categories.
  
  8. Category Filtering
     - Filter accounts by: All, Academic, Personal, Internship, Other.
  
  9. Creation Date Tracking
     - Each account shows when it was created.
     - Helps track password age.

III. Technologies Used (With Justification)
  - Python – Main programming language used to build the system logic.
  - JSON – Used to store account data in a structured and readable format.
  - Regular Expressions (re module) – Used for password validation and strength checking.
  - Tkinter – Built-in Python GUI library for the graphical interface.
  - Pyperclip – Cross-platform clipboard functionality (BSD-3-Clause license).
  - Git – Version control system used to track project changes.
  - GitHub – Repository hosting and collaboration platform.
  - Visual Studio Code – Development environment used to write and manage code.

IV. Detailed Methodology:

  - How Core Features Were Implemented
    The password keeper was implemented using Python functions that allow users to input account information and store it in a JSON file.
    The password strength checker uses conditional logic and regex patterns to analyze password complexity and return improvement suggestions.
    The GUI was built with Tkinter and integrates Pyperclip for seamless clipboard operations.
  
  - Key Design Decisions
    1. Chose JSON for simplicity and readability.
    2. Focused on command-line interface first, then added GUI for visual users.
    3. Included Pyperclip directly in the repository to avoid installation steps.
    4. Added password reuse detection to promote better security habits.
    5. Implemented category filtering for better organization.

  - Trade-offs
    1. Did not implement encryption due to current skill level (planned for future).
    2. GUI is basic but functional – can be enhanced in future versions.
   
V. Installation Instructions:

   1. Clone the repository:
      git clone https://github.com/jzdispo2030-coder/CS_CLog-RMe.git

   2. Navigate into the folder:
      cd GateKeeper

   3. Run the program:
      python main.py

   Note: No additional installation required! Pyperclip is included in the repository.

VI. Programming & Computing Ethics
  - This project considers ethical responsibilities in software development.
  - User privacy was considered by limiting stored data to local files only.
  - Open-source tools and technologies were properly credited.
  - Accessibility and simplicity were prioritized in design.
  - The project aligns with principles from the ACM Code of Ethics, particularly regarding privacy and responsible computing.
    
  In developing GateKeeper, we considered important ethical responsibilities in programming. We respected intellectual property by writing our own original code and properly crediting any tools or technologies used, such as Python, ChatGPT, and DeepSeek.

VII. Third-Party Libraries

  ### Pyperclip
  - **License:** BSD-3-Clause
  - **Author:** Al Sweigart
  - **Purpose:** Cross-platform clipboard functionality
  - **Source:** https://github.com/asweigart/pyperclip
  - **License File:** See `LICENSE-pyperclip.txt` in the repository

VIII. References

  Association for Computing Machinery. (2018). ACM Code of Ethics and Professional Conduct. https://www.acm.org/code-of-ethics
  DeepSeek. (2025). DeepSeek AI Assistant [AI tool]. https://www.deepseek.com/
  OpenAI. (2024). ChatGPT (GPT-4) [Large language model]. https://chat.openai.com/
  Sweigart, A. (2024). Pyperclip. https://github.com/asweigart/pyperclip

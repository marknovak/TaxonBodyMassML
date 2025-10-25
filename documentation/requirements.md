**Functional Requirements:**  
REQ-001: The model will return a confidence interval for all predicted body masses.  (high)  
AC: Given a user has input a species name or list of species names, when the predicted body mass is calculated and displayed, then a corresponding confidence interval will also be displayed.  
REQ-002: The webpage will respond to a user’s input by displaying an explanation of how the model came up with the body mass estimate(s)  (i.e. was it predicted or directly sourced from database) (high)  
	AC: Given a user has input a species name or list of species names, when the predicted   
body mass is calculated and displayed, then an explanation of how the prediction was reached will also be displayed.  
REQ-003: The user is able to input multiple search queries (10+) simultaneously (high)  
	AC: Given an input list of 10 species, when a user submits it to the web interface, then the model outputs the mass of said 10 species.  
REQ-004: The web interface will contain an information tab to help novice users. (low)  
REQ-005: The web interface will contain a citations and methods tab. (low)  
REQ-006: The user interface will meet WCAG accessibility requirements (med)

**Non-functional requirements:**  
REQ-007: Transparency: the data used for the model must be public, no private data shall be used. (med)  
REQ-008: Accuracy: the model will have an accuracy of at least 95% of body masses in the same order of magnitude  
AC: Given a set of 100 species that are not already in the database, when a user inputs them into the web interface, then at least 95 must be within the correct order of magnitude.    
REQ-009: Updatability: the architecture must allow changes to the model to account for the addition of new measured body mass data.  
AC: Given a set of new body mass data, when the GitHub is updated with that data, then the workflow should retrain a new model with the new body mass data.    
REQ-010:  Repeatability: the model will give consistent body mass outputs for a given input.  
	AC: Given a particular species or set of species, when a user requests its body mass,   
the output must be the same every time.  
 
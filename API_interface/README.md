# How Our Frontend Talks to the Backend (The "Where Have You Bean?" API Guide)

**The Setup**
We've built this application to be highly flexible. If the backend system isn't fully ready or we just want to test the design, the app can run entirely on its own using a built-in "mock mode". By flipping a simple switch in our project settings, the app pretends to talk to a server and generates fake data. This means our team can keep testing the entire user flow—from reporting to matching—without getting blocked. When we are ready for the real deal, we simply point the app to our local server.

**When Someone Loses an Item**
When a student submits a "Lost Item" form, our app packages up all their details and hands them over to the backend system.

**What we send over:**

* What kind of item it is (the category).


* What it looks like, including a detailed description and a photo.


* Where and exactly when it was last seen.


* The student's name, email, and phone number.



**What we need back immediately:**
To make the experience feel magically fast, we expect the system to reply *instantly* with a list of potential matches. We need these matches ranked from most likely to least likely, complete with a "match score" and the finder's contact info. Receiving this all at once allows us to show the user hopeful results on the very next screen without making them wait for a loading spinner.

**When Someone Finds an Item**
When a good Samaritan finds a lost item, we send the exact same type of descriptive information and photos to the system. This essentially drops the item into our digital lost-and-found box so the AI can start matching it.

**What we need back:**
We just need a quick thumbs-up from the system that includes a unique ID for the new item. This lets us transition the user to a "Thank you, we've logged this!" confirmation screen.

**Handling Typos and Missing Info**
If a user forgets to fill out a mandatory field or types an invalid email address, the system needs to tell us exactly what went wrong. We expect the backend to send back a specific, structured error message (using a standard format called FastAPI Unprocessable Entity). Our app is wired to automatically read that specific message and highlight the exact text box on the screen that the user needs to fix.

Does this plain-English breakdown help clarify the user journey, or would you like to explore how the new "Claim Item" flow fits into this picture?

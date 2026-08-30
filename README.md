***Cream Beans — Smart Campus Lost & Found***

A smarter way to find what you've lost on campus.

Cream Beans is a smart Lost & Found platform for college campuses.

The idea behind it is simple — eliminate the dependency on WhatsApp groups, notice boards, and social media posts to report and find lost items across campus.

With Cream Beans, students can report an item they've lost or found by providing details such as an image, description, location, and time. The system then goes through the available reports and suggests items that could potentially be a match.

**What it does-**
--> Report lost and found items
--> Upload item photos and details
--> Automatically find possible matches
--> Get a match confidence score
--> Submit claims for found items
--> Admin interface for managing reports and claims

**How the matching works-**

Cream Beans compares lost and found reports using multiple factors:

Category
   +
Image Similarity
   +
Description Similarity
   +
Location
   +
Time
   ↓
Matching Engine
   ↓
Possible Matches
   ↓
Match Confidence Score


For image matching, the project uses CLIP, a pre-trained multimodal AI model developed by OpenAI, to generate image embeddings and compare visual similarity between items.

**Basic Flow-**

Lost Item
    ↓
Image + Description + Location + Time
    ↓
Matching Engine
    ↓
Possible Found Items
    ↓
Match Score

**Tech Stack-**

Part	Technologies
Frontend	React · Vite · Tailwind CSS
Backend	Python · FastAPI
Database	PostgreSQL · Supabase
AI / ML	PyTorch · CLIP · Scikit-learn
Status

Currently in development.

Built by Team Cream Beans

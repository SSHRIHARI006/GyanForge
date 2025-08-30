GyanForge: LangChain-Powered Learning Architecture
1. Vision: The Agentic Learning Companion

Our goal is to create an AI system that acts as a personal tutor. It doesn't just generate content; it actively manages a user's learning path. By leveraging LangChain, we can build an AI Agent that reasons about a user's progress and makes intelligent decisions about what to teach next.
2. LangChain-Native System Architecture

The core of the backend is now powered by two key LangChain components: a RAG Chain for content generation and an Agent for managing the learning path.

graph TD
    subgraph User Experience
        A[🚀 User sets Learning Goal] --> B(📚 User Dashboard);
        B --> C{Start Next Module};
        C --> D[📖 Course Page];
        D --> F[📝 Takes Quiz];
    end

    subgraph "Backend (FastAPI + LangChain)"
        F -- Quiz Score & User ID --> G[🧠 **LangChain Agent (Learning Path Engine)**];
        G -- Next Topic --> H[🔍 **LangChain RAG Chain (Content Generation)**];
        H -- Course Content --> D;
    end

    subgraph Data & Tools
        G -- Uses Tool --> J[👤 **Tool: getUserProgress()** <br> Reads from PostgreSQL];
        G -- Uses Tool --> L[🗺️ **Tool: getKnowledgeGraph()** <br> Finds related topics];
        H -- Retrieves from --> K[📚 **Vector DB (Pinecone)**];
    end

    style G fill:#FFD700,stroke:#333,stroke-width:4px
    style H fill:#87CEEB,stroke:#333,stroke-width:2px

3. Key LangChain Components

    LangChain RAG Chain (Content Generation Service):

        What it is: This is a Runnable sequence built using the LangChain Expression Language (LCEL). It chains together all the steps for creating a course.

        How it works: When it receives a topic (e.g., "Python Functions"), it automatically:

            Uses LangChain's TavilySearch and YoutubeLoader to find resources.

            Uses LangChain's Pinecone vector store integration to retrieve relevant text chunks from your database (RAG).

            Formats all this context into a ChatPromptTemplate.

            Sends the final prompt to the Gemini model (ChatGoogleGenerativeAI).

        This replaces our manual content_service.py with a more powerful and concise implementation.

    LangChain Agent (Learning Path Engine):

        What it is: This is the "brain" of your application. It's an AI agent whose goal is to answer the question: "What should this user learn next?"

        How it works: After a user takes a quiz, we invoke this agent. The agent has access to a set of tools that we define:

            getUserProgress(user_id) Tool: A function that connects to your PostgreSQL database and fetches the user's entire learning history (topics covered, quiz scores).

            getKnowledgeGraph(topic) Tool: A function that can determine the prerequisites and next logical topics for any given subject.

        The agent will then reason using these tools. It might think, "The user scored 95% on 'Python Lists'. The knowledge graph says the next topic is 'Python Loops'. The user has not completed 'Python Loops'. Therefore, my final answer is 'Python Loops'." This replaces a complex set of if/else statements with true AI-driven decision-making.


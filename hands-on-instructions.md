# Hands-On Instructions for Agentic AI Systems
### 1. Hands-On: Build a simple summarizer AI Agent

*   **Instructions**
    *   Familiarize yourself with the Agentic AI engine
    *   Familiarize yourself with google-adk
    *   Learn which “ingredients” are necessary to implement this AI agent with google-adk
    *   Build a simple AI agent which summarizes texts/documents
    *   Integrate the file upload button

*   **Explanation**
    This hands-on introduces the foundational steps for developing a text summarization AI agent. It guides the user through understanding the core components of the Agentic AI engine and Google ADK.

*   **Further Details**
    The activity involves practical application of theoretical knowledge to create a functional AI agent. It covers identifying essential elements for agent implementation within the Google ADK framework and integrating a user interface feature for document input.

### 2. Hands-On: Add Google Search Tool

*   **Instructions**
    *   Enable web search in for your AI agent
    *   Add a Google Search Tool to your summarizer AI agent
    *   Understand how tools are implemented in google-adk
    *   Understand how tools are added to AI agents

*   **Explanation**
    This hands-on extends the previously built summarizer agent by incorporating external web search capabilities. It focuses on the practical aspects of tool integration within the Google ADK.

*   **Further Details**
    The task requires understanding how external functionalities are defined and connected to AI agents. It highlights the process of making tools discoverable and usable by the agent through specific prompts and schemas within the Google ADK framework.

### 3. Hands-On: Add MCP Server

*   **Instructions**
    *   Get overview of Python library "mcp"
    *   Design and implement an MCP server to fetch web pages (= request the page's files (HTML, CSS, images, etc.) from a remote server)
    *   Script a Docker file to run the server
    *   Integrate the mcp tool into the summarizer agent

*   **Explanation**
    This activity focuses on establishing a standardized interface for tools through an MCP (Model Context Protocol) server. The goal is to enable the summarizer agent to retrieve web page content efficiently.

*   **Further Details**
    It involves gaining familiarity with the "mcp" Python library, designing a server to handle web page fetching, containerizing the server using Docker for portability, and then integrating this new, standardized tool into the existing summarizer agent architecture.

### 4. Hands-On: Design an AI agent team for a use case of your choice

*   **Instructions**
    *   Think about a use case for an agent team
    *   Design the agent team
    *   Implement the agent team

*   **Explanation**
    This hands-on challenges users to conceptualize, design, and implement a multi-agent system. It encourages applying knowledge of agent collaboration to a specific use case.

*   **Further Details**
    The exercise involves defining roles and responsibilities for multiple AI agents, establishing communication protocols (e.g., hierarchical or graph-based), and orchestrating their interactions to solve a more complex problem than a single agent could handle.

### 5. Hands-On: Communicate with external agent

*   **Instructions**
    *   Get overview of Python library "A2A"
    *   Implement an evaluation/critique agent for your summarizer agent as external agent
    *   Write Dockerfile to run it locally
    *   Deploy it to HuggingFace
    *   Add it as evaluation after the summarizer

*   **Explanation**
    This activity explores inter-agent communication using the A2A (Agent-to-Agent) protocol. The practical application involves creating an external agent to critique the summarizer's performance.

*   **Further Details**
    It covers understanding the "A2A" Python library, building a dedicated critique agent, containerizing it with Docker, deploying it to a platform like HuggingFace, and integrating it into the workflow to provide automated evaluation of the summarization output.

### 6. Hands-On: Investigate state and session

*   **Instructions**
    *   Save and load state variables
    *   Log and investigate the session

*   **Explanation**
    This hands-on focuses on the critical aspects of state management and session persistence in Agentic AI systems. It aims to teach how agents maintain context over time.

*   **Further Details**
    Users will learn techniques for saving and loading variables that define an agent's state across interactions and how to log and analyze session data to understand the flow of conversation and task progression.

### 7. Hands-On: Add memory bank

*   **Instructions**
    *   Implement a memory service based on the VertexAIMemoryBank
    *   Implement and/or add built-in tools to memorize the session and load the memories into the chat

*   **Explanation**
    This activity introduces the concept of long-term memory for AI agents, specifically using Google's VertexAIMemoryBank. It aims to enable agents to retain and recall information across multiple sessions.

*   **Further Details**
    It involves setting up and integrating a memory service to allow agents to store important facts and preferences, thereby facilitating personalized and more informed interactions over extended periods.

### 8. Hands-On: Add artifact service

*   **Instructions**
    *   Implement artifact service over Google Cloud Storage
    *   Implement save artifact tool for markdown and pdf documents
    *   Add save and load artifact tools to your agent team

*   **Explanation**
    This hands-on focuses on managing diverse data types (artifacts) beyond plain text within an Agentic AI system. It details the implementation of a service for structured storage and retrieval of these artifacts.

*   **Further Details**
    The activity involves leveraging Google Cloud Storage to create a robust artifact service, developing specific tools for saving and loading documents like markdown and PDFs, and integrating these tools within the agent team for efficient data handling.

### 9. Hands-On: Add RAG

*   **Instructions**
    *   Implement Vertex AI Rag Engine
    *   Add tool to access Vertex AI Rag Engine to agent team
    *   Add sample corpus suitable for your agent teams

*   **Explanation**
    This hands-on guides users in integrating Retrieval-Augmented Generation (RAG) into their AI agents. The goal is to enhance factual accuracy and provide agents with access to dynamic, up-to-date information.

*   **Further Details**
    It involves deploying the Vertex AI RAG Engine, creating tools that allow agents to query this engine for relevant information, and preparing a suitable corpus of documents for retrieval to ground agent responses.

### 10. Hands-On: Investigate ADK Runner Implementation

*   **Instructions**
    *   Use your Coding Agent to investigate the implementation of the ADK runner

*   **Explanation**
    This activity promotes a deeper understanding of the Agent Development Kit's (ADK) runtime environment. It suggests using another AI agent (a "Coding Agent") to analyze and comprehend the underlying implementation.

*   **Further Details**
    This exercise emphasizes advanced debugging and analysis techniques, potentially involving code walkthroughs and interpretation facilitated by an AI, to demystify the execution flow of ADK-based agents.

### 11. Hands-On: Investigate Backend Architecture

*   **Instructions**
    *   Investigate FastAPI backend
    *   Investigate Websocket connection, which pushes the agent's response to the UI

*   **Explanation**
    This hands-on focuses on exploring the backend architecture commonly used for Agentic AI systems, specifically the integration of FastAPI for APIs and WebSockets for real-time communication.

*   **Further Details**
    It involves examining how FastAPI handles API requests and responses, and how WebSocket connections are utilized to provide a continuous, bidirectional communication channel for pushing agent responses to the user interface efficiently.

### 12. Hands-On: Deploy on Cloud Run

*   **Instructions**
    *   Implement necessary Google Cloud Run scripts
        *   service.yaml
        *   cloudbuild.yaml
        *   Dockerfile
    *   Deploy your application in Google Cloud Run
    *   Scale your application

*   **Explanation**
    This hands-on provides practical experience in deploying Agentic AI applications using Google Cloud Run, a fully managed serverless platform.

*   **Further Details**
    The activity includes creating essential configuration files for containerization and deployment (service.yaml, cloudbuild.yaml, Dockerfile), performing the actual deployment to Cloud Run, and understanding how to manage the application's scaling for performance and cost efficiency.

### 13. Hands-On: Investigate GCP Logging & Monitoring

*   **Instructions**
    *   Investigate existing GCP services for logging, metrics, tracing and audit logs
    *   Setup OpenTelemetry in ADK and GCP

*   **Explanation**
    This hands-on focuses on establishing comprehensive observability for Agentic AI systems deployed on Google Cloud Platform. It covers logging, monitoring, and tracing.

*   **Further Details**
    It involves exploring GCP's built-in services for capturing application and system logs, monitoring metrics, and setting up OpenTelemetry for detailed end-to-end tracing of agent actions, tool calls, and LLM interactions for debugging and performance analysis.

### 14. Hands-On: Perform evaluation

*   **Instructions**
    *   Add a simple evaluation case to one of your agents
    *   The two key schema files are Eval Set and Eval Case
    *   Use adk web - Run Evaluations via the Web UI

*   **Explanation**
    This final hands-on emphasizes the importance of evaluating AI agents. It guides users through setting up and running evaluations using the ADK's built-in framework.

*   **Further Details**
    The activity involves creating specific test scenarios (`Eval Set` and `Eval Case` schema files) and then utilizing the ADK web interface to execute these evaluations. This helps in assessing the agent's performance, correctness, and adherence to expected behavior.


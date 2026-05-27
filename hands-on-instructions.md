# Hands-On Instructions for Agentic AI Systems

## Hands-On 1: Build a Simple Summarizer AI Agent

### Clear Instructions:
*   Familiarize yourself with the Agentic AI engine.
*   Familiarize yourself with Google ADK (Agent Development Kit).
*   Learn which "ingredients" are necessary to implement this AI agent with Google ADK.
*   Build a simple AI agent that summarizes texts/documents.
*   Integrate a file upload button.

### Explanation and Further Details:
This initial hands-on project is designed to introduce the core concepts of building an agentic AI system. Participants will learn to utilize the Agentic AI engine and the Google Agent Development Kit (ADK) to construct a basic AI agent capable of summarizing text. A key part of this involves understanding the components needed for such an agent (e.g., perception, reasoning, action, learning) and implementing a user interface element, specifically a file upload button, to facilitate interaction with the summarizer. This task aligns with the overall "develop, build, test, and explore" lifecycle for Agentic AI systems.

---

## Hands-On 2: Add Google Search Tool

### Clear Instructions:
*   Enable web search for your AI agent.
*   Add a Google Search Tool to your summarizer AI agent.
*   Understand how tools are implemented in Google ADK.
*   Understand how tools are added to AI agents.

### Explanation and Further Details:
This hands-on extends the functionality of the summarizer agent by incorporating external tools. A tool is defined as an external capability that an AI agent can invoke to perform specific actions beyond its inherent text generation abilities, such as accessing real-world data, conducting complex computations, or interacting with external systems. The focus here is on integrating a Google Search tool. This integration allows the agent to query the web for up-to-date information, retrieve relevant documents, news, and facts, thereby enhancing its knowledge base and ability to answer current or unknown questions.

---

## Hands-On 3: Add MCP Server

### Clear Instructions:
*   Get an overview of the Python library "mcp".
*   Design and implement an MCP server to fetch web pages (request HTML, CSS, images, etc. from a remote server).
*   Script a Dockerfile to run the server.
*   Integrate the `mcp` tool into the summarizer agent.

### Explanation and Further Details:
This section focuses on the infrastructure and standardization necessary for integrating various tools into AI agents. An MCP (Model Context Protocol) server acts as a standardized interface, allowing AI agents to access diverse tools, data, and capabilities in a consistent manner. The benefits of using an MCP server include preventing custom, one-off integrations, enabling plug-and-play connectivity across different ecosystems, and making agents more modular, scalable, and maintainable. The task specifically involves building an MCP server for fetching web page content and making this functionality available to the summarizer agent. The server architecture for `fetch_url()` illustrates how an agent interacts with the MCP server, which then uses an HTTP client (`httpx`) to retrieve data from external web pages.

---

## Hands-On 4: Investigate State and Session

### Clear Instructions:
*   Save and load state variables.
*   Log and investigate the session.

### Explanation and Further Details:
This hands-on delves into the concepts of short-term memory through "sessions" and "state" within an agentic AI system. A session acts as a container for a single user-agent conversation, maintaining a chronological list of interactions (user messages, agent responses, tool actions) and the current state. The state, described as the agent's dedicated "scratchpad," stores serializable key-value pairs to personalize interactions, track task progress, accumulate information, and make informed decisions. This exercise focuses on understanding how to manage this short-term memory by saving, loading, logging, and investigating the variables and flow within a session.

---

## Hands-On 5: Design an AI Agent Team

### Clear Instructions:
*   Think about a use case for an agent team.
*   Design the agent team.
*   Implement the agent team.

### Explanation and Further Details:
Moving beyond single agents, this hands-on task introduces the concept of multi-agent systems, or "agent teams." The document describes two versions of agent communication within an ADK team. ADK v1 features a hierarchical, tree-like structure where agents communicate strictly with parent and child agents, ensuring clear separation of concerns and predictable communication paths. ADK v2 introduces a more flexible, graph-based structure allowing multiple connections and dynamic routing, enabling complex coordination patterns like conditional workflows, parallel processing (fan-out/fan-in), and iterative refinement loops. This exercise encourages users to conceptualize, design, and implement a system where multiple specialized agents collaborate to achieve a more complex objective than a single agent could handle.

---

## Hands-On 6: Communicate with External Agent

### Clear Instructions:
*   Get an overview of the Python library "A2A".
*   Implement an evaluation/critique agent for your summarizer agent as an external agent.
*   Write a Dockerfile to run it locally.
*   Deploy it to HuggingFace.
*   Add it as evaluation after the summarizer.

### Explanation and Further Details:
This hands-on focuses on enabling communication and interoperability between "external" agents using an A2A (Agent-to-Agent) protocol. The A2A protocol aims to transform isolated agent systems into a connected and interoperable network. Key benefits include facilitating agent-to-agent communication across system boundaries, integrating with external services and platforms, standardizing task and context exchange, enabling decoupled integration, and ensuring secure communication. Typical use cases include collaborating with third-party agents, integrating domain-specific expert agents, and extending internal agent teams with external capabilities. For this task, participants will build and deploy an independent evaluation or critique agent (e.g., on HuggingFace) to assess the performance of the previously built summarizer agent, showcasing external agent interaction.

---

## Hands-On 7: Add Memory Bank

### Clear Instructions:
*   Implement a memory service based on the VertexAIMemoryBank.
*   Implement and/or add built-in tools to memorize the session and load the memories into the chat.

### Explanation and Further Details:
This final hands-on explores the implementation of long-term memory in AI agents, often referred to as a "Memory Bank." Unlike short-term memory (sessions) which is temporary, long-term memory persists across multiple conversations and even application restarts. A Memory Bank is crucial for long-term personalization, allowing agents to remember user preferences, historical interactions, and key details over extended periods. It supports LLM-driven knowledge extraction by automatically identifying and persisting important information, making the agent's context dynamic and evolving rather than static (as with RAG). The task involves implementing a memory service, potentially using Google's VertexAIMemoryBank, and creating tools to both save session memories and load them into new conversations, ensuring the agent has access to a continuously updated and relevant knowledge base.


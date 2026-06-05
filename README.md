# 🌌 Astronomy AI Agent with Custom Function Tools

This project demonstrates how to build an AI agent using **Microsoft Foundry Agent Service** that integrates **custom function tools** to extend agent capabilities.

The agent acts as an **astronomy assistant** that can:
- Provide information about astronomical events 🌠  
- Calculate telescope rental costs based on user input 🔭  
- Dynamically call Python functions during conversations  

---

## 🚀 Features

- Custom function tool integration with AI agents  
- Function calling workflow using Azure AI Foundry  
- Real-world astronomy assistant use case  
- Dynamic telescope rental cost calculator  
- End-to-end agent + tool execution pipeline  

---

## 🧠 How It Works

1. User sends a query (astronomy info or rental request)
2. The agent decides whether a function tool is needed
3. A Python function is executed via tool calling
4. The result is returned in natural language form

---

## 🛠️ Tech Stack

- Microsoft Foundry Agent Service  
- Azure AI Agent SDK  
- Python  
- Function Calling (Tool Use)  

---

## 📦 Example Use Cases

- “When is the next meteor shower?”  
- “How much will it cost to rent a telescope for 3 nights?”  
- “Tell me about upcoming lunar eclipses”  

---

## 📚 Learning Objectives

- Build AI agents with custom tools  
- Implement function calling workflows  
- Extend agent capabilities with Python logic  
- Understand tool-based agent architecture  

---
## .env

Needs two variables:
- AZURE_PROJECT_ENDPOINT= your-project-link
- MODEL_DEPLOYMENT_NAME="model-deployment"

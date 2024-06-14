# Financial Advisor Chatbot

## Overview
This repository contains the code for a customized Retrieval-Augmented Generation (RAG) chatbot, developed for the AI Hackathon. The chatbot utilizes OpenAI's GPT-4.0 to offer personalized financial advice and trading support. It integrates various reliable data sources to ensure accurate and user-specific financial guidance.

## Features
- **Personalized Financial Advice**: Delivers tailored advice based on the user's experience level and financial data.
- **Interactive Trading**: Allows users to perform trading actions directly through the chat interface, ideal for beginners.
- **Multi-Source Data Integration**: Leverages an autonomous agent to fetch up-to-date and reliable financial information from multiple sources.
- **Regulatory Compliance**: Ensures all financial recommendations are in line with current trading regulations.

## Tech Stack
- **Language Model**: OpenAI's GPT-4.0 API
- **Vector Database**: Options include Quadrant or Datastax (to be finalized)
- **Backend**: Node.js or Python Flask (to be decided)
- **Frontend**: React for a responsive and intuitive user interface

## Getting Started

### Prerequisites
- Node.js or Python environment (depending on final backend choice)
- React installed on your machine

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/JYe9/Quadcode_FinBot_team.git
   ```
2. Navigate to the project directory:
   ```
   cd Quadcode_FinBot_team
   ```
3. Install dependencies:
   ```
   npm install  # If using Node.js
   pip install -r requirements.txt  # If using Python
   ```

### Running the Application
1. Start the backend server:
   ```
   node server.js  # For Node.js
   python app.py   # For Python Flask
   ```
2. Launch the frontend:
   ```
   cd frontend
   npm start
   ```

## Contribution
Please fork the repository and submit pull requests to the `main` branch. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments
- OpenAI for providing the GPT-4.0 API
- Hackathon organizers and participants for their invaluable insights and feedback

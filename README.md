# NAO Robot Interaction Using NLP and BERT

## Project Overview
This project aims to enhance the interaction capabilities of the NAO robot using Natural Language Processing (NLP) and the BERT model (Bidirectional Encoder Representations from Transformers). The goal is to enable NAO to understand and respond to human language more effectively, providing a more natural and engaging experience.

## Features
- **Natural Language Understanding**: Using BERT to comprehend and process user input.
- **Interactive Responses**: NAO generates responses based on the processed input.
- **Flask Server**: A server to handle the communication between the user and the NAO robot.
- **Extensible Architecture**: Easily extendable for additional functionalities and improvements.
- **Comparison of Responses**: The system compares BERT's direct and concise answers with detailed information from the corpus.

## Installation
To get started with this project, follow these steps:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/your-username/Conversation-NAO-Children-using-NLP-BERT.git
    cd Conversation-NAO-Children-using-NLP-BERT
    ```

2. **Create virtual environments for different Python versions**:

  - **Python 3.12 for Flask Server**:
        ```sh
        pyenv install 3.12.0
        pyenv virtualenv 3.12.0 flask-env
        pyenv activate flask-env
        pip install -r requirements.txt
        ```

  - **Python 2.7 for Naoqi**:
        ```sh
        pyenv install 2.7.18
        pyenv virtualenv 2.7.18 naoqi-env
        pyenv activate naoqi-env
        pip install naoqi
        ```

  - **Python 3.9 for Speech Recognition**:
        ```sh
        pyenv install 3.9.0
        pyenv virtualenv 3.9.0 speech-env
        pyenv activate speech-env
        pip install -r requirements.txt
        ```

## Usage
-Run the Flask server** (Python 3.12):
-Use the script for NAO interaction (Python 2.7):
-Use the script for speech recognition (Python 3.9):

## How It Works
-Question Input: The system receives a question via the Flask server.
-BERT Response: The question is processed using a BERT model to generate a concise answer.
-Corpus Analysis: The system analyzes the corpus to find the detailed context that best matches BERT's response.
-Response Comparison: BERT's concise answer is printed, and the detailed context is spoken by the NAO robot using the `tts.say` method.

## Example Interaction
1. **Question**: "What is the capital of France?"
2. **BERT Answer**: "Paris" (printed)
3. **Detailed Answer**: "Paris is the capital and most populous city of France." (spoken by NAO)

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or new features.




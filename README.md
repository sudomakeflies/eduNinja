# ![eduNinja logo](static/logo.svg) eduNinja

**eduNinja** is the culmination of years of self-directed and self-funded research, emerging as a comprehensive system for personalized learning support. Focused on a "prioritized assessment" and "offline-first" approach, eduNinja emphasizes STEAM (Science, Technology, Engineering, Arts, and Mathematics). It offers optimized multiple-choice assessments for mathematics and science, integrating an AI-assisted feedback and recommendation system to provide an adaptive and effective learning experience.

## 🚀 eduNinja-Evals

**eduNinja-Evals** facilitates the creation and management of multiple-choice assessments in mathematics and science (STEAM). It allows users to take assessments with instant feedback using a locally deployed machine learning language model via Ollama or Claude 3.5 Sonnet through Anthropic API for AI-assisted feedback.

### Key Features:

- **Course & Assessment Management:** Create and manage courses, questions, and assessments.
- **Instant Feedback:** Take assessments with immediate AI-assisted feedback.
- **AI Integration:** Leverage language models for feedback via Ollama or Anthropic API.
- **Account Management:** Includes functionality for user registration and login.
- **LaTeX Rendering:** High-quality equation rendering for a better learning experience.
- **Question Bank:** Access an extensive question bank for assessments.

### Upcoming Features:
- **Personalized Learning System:** Currently a placeholder, with plans for full implementation soon.

## 🔧 eduNinja-PL

**eduNinja-PL** is a personalized learning support system. Based on user-declared preferences and diagnostic tests, it provides recommendations and feedback from LLMs (Large Language Models).

## 🛠️ Installation & Usage

1. **Install Docker.**
2. **Clone this repository:**
    ```bash
    git clone https://github.com/sudomakeflies/eduNinja.git
    ```
3. **Navigate to the project directory:**
    ```bash
    cd eduNinja
    ```
4. **Copy the example environment file and customize it with your API keys:**
    ```bash
    mv .env_example .env
    ```
5. **Build and run the project:**
    ```bash
    docker-compose up --build
    ```

6. **Access the application on localhost and start exploring!**

## 🤝 Contribution

Contributions are welcome! If you have ideas for new features, bug fixes, or code improvements, feel free to open an issue or submit a pull request.

## 📝 License

This project is licensed under the GPLv3 License.

# 🥊 MMA AI

Welcome to **MMA AI** – your ultimate tool for predicting the outcomes of mixed martial arts (MMA) fights using data-driven insights and artificial intelligence. With a focus on UFC fighters, this app lets you research fighters, analyze their fight history, and generate predictions on potential matchups.

## Features

- **Fighter Research**: Select two fighters and view detailed information about their fight history, including win/loss streaks, recent fights, and more.
- **Fight Predictions**: Generate predictions for potential matchups using AI, including details on who is likely to win, the method of victory, and a detailed explanation.
- **Visual Analytics**: View interactive charts showing fighters' performance metrics, such as the breakdown of wins by KO, submission, or decision.
- **Data-Driven Reports**: Generate and download comprehensive reports summarizing the prediction results.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/mma-ai.git
   ```

2. Navigate to the project directory:

   ```bash
   cd mma-ai
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare the Data**: Ensure you have the necessary CSV files (`fighter_info.csv` and `event_data_sherdog.csv`) in the `data/` directory.

2. **Run the App**:

   ```bash
   streamlit run app.py
   ```

3. **Interact with the App**:
   - Select fighters from the dropdown menus.
   - Click "Predict the Fight" to generate predictions.
   - Download reports by clicking "Generate Report."

## Data Sources

- **Fighter Information**: Data includes general fighter information such as birth date, nationality, association, weight class, height, wins, losses, and more.
- **Event Data**: Historical fight data, including event names, fight results, and performance metrics.

## Dependencies

- `streamlit`: For building and running the web app.
- `pandas`: For data manipulation and analysis.
- `plotly`: For creating interactive visualizations.
- `openai`: For generating AI-based predictions.

## Future Enhancements

- **Enhanced Predictions**: Improve the AI model to provide even more accurate predictions.
- **Additional Metrics**: Incorporate more detailed fight metrics like significant strikes, takedowns, etc.
- **User Authentication**: Add user authentication to personalize the experience and save prediction history.

## Contributing

We welcome contributions from the community. Feel free to fork the repository, create a new branch, and submit a pull request.

## Contact

Created by Tyler Durette. Feel free to reach out at [tyler.durette@gmail.com](mailto:tyler.durette@gmail.com) or check out [my GitHub profile](https://github.com/bestisblessed).

---

MMA AI © 2024 | [GitHub](https://github.com/bestisblessed)

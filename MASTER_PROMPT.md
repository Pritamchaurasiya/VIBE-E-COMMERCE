# Master Prompt & Future Roadmap

## Completed Features
- **Weather Widget**: Real-time weather updates for farmers.
- **Soil Health Analysis**: Recommendations based on N-P-K-pH values.
- **Loyalty Points (Coins)**: Reward system for purchases.
- **Vendor Analytics**: Detailed sales dashboard for vendors.
- **Security Enhancements**: CSP, Dependency updates.

## Suggested Future Features (Next Steps)

1.  **AI-Powered Crop Disease Detection** 🍃
    *   **Goal**: Allow users to upload photos of their crops (leaves) to detect diseases automatically.
    *   **Tech**: TensorFlow.js (Frontend) or PyTorch/TensorFlow (Backend).
    *   **Value**: Immediate, actionable advice for farmers.

2.  **Community Forum / Knowledge Hub** 🗣️
    *   **Goal**: A space for farmers and experts to discuss crop issues, share tips, and ask questions.
    *   **Tech**: New Django App `community`, threaded comments, upvoting.
    *   **Value**: Increases user engagement and retention.

3.  **Logistics & Tracking Integration** 🚚
    *   **Goal**: Real-time order tracking via third-party logistics (e.g., ShipRocket, Delhivery).
    *   **Tech**: Webhook integration, Tracking API.
    *   **Value**: Transparency and trust for buyers.

4.  **Multilingual Voice Search** 🎤
    *   **Goal**: Enhance the search bar to understand voice commands in Hindi and regional languages.
    *   **Tech**: Web Speech API with language selection or Google Cloud Speech-to-Text.
    *   **Value**: Accessibility for users less comfortable with typing.

5.  **Farm Management Tools** 🚜
    *   **Goal**: Tools to calculate seed rate, fertilizer dosage, and profit estimation.
    *   **Tech**: Interactive React calculators.
    *   **Value**: Utility tools that bring users back daily.

## Maintenance & Optimization
- **Frontend Migration**: Consider migrating from CRA (Create React App) to Vite for faster builds and better ESM support.
- **Testing**: Expand test coverage for Frontend components using React Testing Library.
- **Performance**: Implement Redis caching for product lists and search results.

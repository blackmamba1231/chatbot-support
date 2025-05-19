<<<<<<< HEAD
# Chatbot Support

A comprehensive chatbot solution for customer support and assistance.

## Installation Guide

### Prerequisites

- [Node.js](https://nodejs.org/) (v16 or later)
- [npm](https://www.npmjs.com/) (v8 or later) or [yarn](https://yarnpkg.com/) (v1.22 or later)
- [Git](https://git-scm.com/) for version control

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/chatbot-support.git
   cd chatbot-support
   ```

2. **Install dependencies**

   Using npm:
   ```bash
   npm install
   ```

   Or using yarn:
   ```bash
   yarn install
   ```

3. **Environment Configuration**

   Create a `.env` file in the root directory and add the following variables:
   ```
   PORT=3000
   NODE_ENV=development
   # Add any API keys or other environment variables here
   ```

4. **Start the development server**

   ```bash
   npm run dev
   ```
   
   Or using yarn:
   ```bash
   yarn dev
=======
# Vogo.Family Mall Delivery Chatbot

An AI-powered chatbot platform for Vogo.Family, supporting mall delivery, shopping, and customer support across web and mobile.

## Features

- 🤖 AI-powered chat (GPT-3.5/4, RAG)
- 🗣️ Voice messaging with Whisper transcription
- 🛍️ Mall delivery from multiple Romanian cities
- 🏪 Real-time WooCommerce product catalog
- 📧 Order confirmation emails
- 💳 Secure payment processing
- 📍 Location-based recommendations
- 🛒 Shopping cart & order
- 🔍 Product search
- 📦 Order tracking
- 🖥️ Modern web & 📱 mobile UI

---

## Prerequisites

- [Node.js](https://nodejs.org/) (v18+ recommended)
- [Python](https://python.org/) (v3.9+)
- [Git](https://git-scm.com/)
- [Android Studio](https://developer.android.com/studio) (for mobile dev)
- [OpenAI API Key](https://platform.openai.com/)
- [WooCommerce Store](https://woocommerce.com/) API credentials

---

## 1. Clone the Repository

   ```bash
   cd apps/backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start the Frontend**
   ```bash
   cd apps/fe
   npm run dev
   ```

3. Access the application at http://localhost:3000

## Testing

```bash
# Backend tests
cd apps/backend
pytest

# Frontend tests
cd apps/fe
npm test
```

## Supported Locations

The chatbot currently supports mall delivery services in the following Romanian cities:

1. Alba Iulia
   - Alba Mall

2. Arad
   - Atrium Mall

3. Miercurea Ciuc
   - Nest Park Retail

4. Vaslui
   - Proxima Shopping Center

5. Târgu Mureș
   - PlazaM Târgu Mureș

6. Suceava
   - Iulius Mall Suceava
   - Shopping City Suceava

7. Târgu-Jiu
   - Shopping City Târgu-Jiu

## Product Categories

1. Kids Activities
   - Educational toys and learning materials
   - Children's activity sets and games
   - Creative arts and crafts supplies

2. Bio Food
   - Organic produce and vegetables
   - Natural and organic snacks
   - Gluten-free products

3. Antipasti
   - Italian appetizers and starters
   - Mediterranean olives and tapenades
   - Cured meats and cheeses

4. Pet Care
   - Premium pet food and treats
   - Pet grooming supplies
   - Pet health supplements

5. Allergy Products
   - Hypoallergenic food items
   - Allergy-friendly snacks
   - Gluten-free alternatives

## Implementation Status

- [x] AI-powered chat interface
- [x] Voice message transcription
- [x] WooCommerce integration
- [x] Mall delivery service
- [x] Product categories and filtering
- [x] Location-based services
- [x] Order processing
- [x] Email notifications
- [ ] Payment gateway integration
- [ ] Order tracking system

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential. © 2025 Vogo.Family
>>>>>>> 9c26091 (backend try)
   ```

   The server should now be running at `http://localhost:3000`

## Project Structure

```
chatbot-support/
├── src/               # Source code
├── public/            # Static assets
├── config/            # Configuration files
├── tests/             # Test files
└── package.json       # Project dependencies and scripts
```

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the project for production
- `npm run start` - Start the production server
- `npm run test` - Run the test suite

## Deployment

Instructions for deploying to production environments:

1. Build the project:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm run start
   ```

## Additional Resources

- [Documentation](https://example.com/docs)
- [API Reference](https://example.com/api)
- [Contributing Guidelines](https://example.com/contributing)

## Support

For questions or issues, please open an issue on the GitHub repository or contact the development team at support@example.com.

## Updates from freelancer:
.\venv\Scripts\activate

pip install -r requirements.txt

python main.py

http://localhost:3000


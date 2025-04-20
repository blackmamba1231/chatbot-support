# Vogo.Family Mall Delivery Chatbot

An AI-powered chatbot for Vogo.Family mall delivery services, providing seamless shopping experience across multiple Romanian cities.

## Features

- 🤖 AI-powered chat interface with GPT integration
- 🗣️ Voice messaging with Whisper transcription
- 🛍️ Mall delivery from multiple locations
- 🏪 Real-time product catalog from WooCommerce
- 📧 Order confirmation emails
- 💳 Secure payment processing
- 📍 Location-based product recommendations
- 🛒 Shopping cart functionality
- 🔍 Product search and filtering
- 📦 Order tracking and management

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [Python](https://python.org/) (v3.9 or later)
- [Git](https://git-scm.com/)
- [WooCommerce Store](https://woocommerce.com/) with API access
- [OpenAI API Key](https://platform.openai.com/) for GPT and Whisper

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/blackmamba1231/chatbot-support.git
   cd chatbot-support
   ```

2. **Backend Setup**
   ```bash
   cd apps/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Update with your credentials
   ```

3. **Frontend Setup**
   ```bash
   cd ../fe
   npm install
   cp .env.example .env  # Update with your credentials
   ```

4. **Environment Configuration**

   Update the following files with your credentials:
   - `apps/backend/.env`:
     ```env
     OPENAI_API_KEY=your_api_key
     WP_API_URL=https://your-store.com
     WP_CONSUMER_KEY=your_woocommerce_key
     WP_CONSUMER_SECRET=your_woocommerce_secret
     SMTP_USERNAME=your_email@vogo.family
     SMTP_PASSWORD=your_email_password
     ```

5. **Google Calendar Setup**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Calendar API
   - Download credentials.json and place it in `apps/backend/`

## Running the Application

1. **Start the Backend**
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


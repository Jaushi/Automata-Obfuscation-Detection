# Automata Obfuscation Detection

A full-stack web application for detecting and analyzing obfuscated code patterns using machine learning and pattern recognition.

## Tech Stack

### Frontend
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

### Backend
- **Python Flask** - Lightweight web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Python-dotenv** - Environment variable management

## Project Structure

```
Automata-Obfuscation-Detection/
├── client/                 # Frontend React application
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── types/         # TypeScript type definitions
│   │   ├── utils/         # Utility functions and API client
│   │   ├── App.tsx        # Main App component
│   │   ├── main.tsx       # Application entry point
│   │   └── index.css      # Global styles with Tailwind
│   ├── index.html         # HTML template
│   ├── package.json       # Frontend dependencies
│   ├── tsconfig.json      # TypeScript configuration
│   ├── vite.config.ts     # Vite configuration
│   └── tailwind.config.js # Tailwind CSS configuration
│
├── server/                # Backend Flask application
│   ├── app/
│   │   ├── routes/        # API route handlers
│   │   ├── services/      # Business logic and detection algorithms
│   │   ├── models/        # Data models
│   │   └── utils/         # Helper functions
│   ├── tests/             # Unit and integration tests
│   ├── run.py             # Application entry point
│   └── requirements.txt   # Python dependencies
│
└── README.md              # This file

```

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

6. Run the Flask server:
```bash
python run.py
```

The backend API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check if the API is running

### Detection
- **POST** `/api/detect` - Analyze code for obfuscation patterns
  ```json
  {
    "code": "string",
    "language": "string (optional)"
  }
  ```

## Development

### Frontend Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend
- The Flask server runs in debug mode by default during development
- Add new routes in `server/app/routes/`
- Add business logic in `server/app/services/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Authors

- Your Name - Initial work
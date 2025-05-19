import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get port from env or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting Vogo.Family AI Chatbot Backend on {host}:{port}")
    print("API documentation available at:")
    print(f"  • Swagger UI: http://localhost:{port}/docs")
    print(f"  • ReDoc: http://localhost:{port}/redoc")
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)

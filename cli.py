import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="HolonIngest Server Runner")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for dev mode")
    
    args = parser.parse_args()

    print(f"🚀 Starting HolonIngest Engine on http://{args.host}:{args.port}")
    
    # Imports the FastAPI 'app' object from your gateway module
    uvicorn.run(
        "holoningest.decoder_gateway:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()

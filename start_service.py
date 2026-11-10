import sys
import uvicorn

if __name__ == "__main__":
    # args: app_dir, port
    app_dir = sys.argv[1]
    port = int(sys.argv[2])
    sys.path.insert(0, app_dir)
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)

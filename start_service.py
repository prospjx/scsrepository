import importlib
import os
import sys
import uvicorn

if __name__ == "__main__":
    app_dir = sys.argv[1]
    port = int(sys.argv[2])

    # 1. Change working directory directly into the service folder
    os.chdir(app_dir)
    # 2. Add to both sys.path and PYTHONPATH
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    os.environ["PYTHONPATH"] = app_dir + ":" + os.environ.get("PYTHONPATH", "")

    # 3. Import the FastAPI app object directly in-process so string resolution cannot fail
    module = importlib.import_module("src.main")
    app_obj = getattr(module, "app")

    # 4. Pass the actual app object to uvicorn directly
    uvicorn.run(app_obj, host="0.0.0.0", port=port)

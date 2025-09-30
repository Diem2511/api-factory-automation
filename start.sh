#!/bin/bash
python -c "
import os
import uvicorn
from main import app

port = int(os.getenv('PORT', 8000))
print(f'Starting server on port {port}...')
uvicorn.run(app, host='0.0.0.0', port=port)
"

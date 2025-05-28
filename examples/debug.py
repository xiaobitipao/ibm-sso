import os
import sys

import uvicorn
from dotenv import load_dotenv

load_dotenv()

# ################################################################################
# Add ibm-sso
# ################################################################################

# Set the project root directory
# project_root_dir = f'{os.environ["HOME"]}/0/Project/20991231_Z_Private/public/ibm-sso/'
project_root_dir = "../"

# Get the ibm_sso module directory
ibm_sso_module_dir_1 = os.path.join(project_root_dir, "src")

# Get the ibm_sso module directory
ibm_sso_module_dir_2 = os.path.join(project_root_dir, "src", "ibm_sso")

# Add the ibm_sso module directory to sys.path
sys.path.append(ibm_sso_module_dir_1)
sys.path.append(ibm_sso_module_dir_2)


# ################################################################################
# Add src
# ################################################################################
sys.path.append("./src")


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        # ssl_keyfile="./ssl_local/key.pem",
        # ssl_certfile="./ssl_local/cert.pem",
    )

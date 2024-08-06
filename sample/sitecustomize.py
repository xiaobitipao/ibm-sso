import os
import sys

# Set the project root directory
project_root_dir = f'{os.environ["HOME"]}/0/Project/20991231_Z_Private/public/ibm-sso/'

# Get the ibm_sso module directory
ibm_sso_module_dir_1 = os.path.join(project_root_dir, 'src')

# Get the ibm_sso module directory
ibm_sso_module_dir_2 = os.path.join(project_root_dir, 'src', 'ibm_sso')

# Add the ibm_sso module directory to sys.path
sys.path.append(ibm_sso_module_dir_1)
sys.path.append(ibm_sso_module_dir_2)

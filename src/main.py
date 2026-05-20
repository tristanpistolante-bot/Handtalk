from database import create_database
from login import launch_login
 
# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
 
    # make sure database + tables exist
    create_database()
 
    # open login window first
    launch_login()
 
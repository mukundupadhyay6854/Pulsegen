import subprocess
import sys
import os

def install_requirements():
    print("Installing required packages...")
    print("This may take a few minutes, especially for sentence-transformers...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n[OK] All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error installing packages: {e}")
        return False

def init_database():
    print("\nInitializing database...")
    try:
        from db.init_db import init_database
        init_database()
        print("[OK] Database initialized!")
        return True
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        return False

def main():
    print("="*60)
    print("Agentic App Review Trend Analysis - Setup")
    print("="*60)
    
    if not install_requirements():
        print("\nSetup failed. Please install packages manually:")
        print("  pip install -r requirements.txt")
        return
    
    if not init_database():
        print("\nWarning: Database initialization failed.")
        print("You can initialize it manually with: python db/init_db.py")
        return
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)
    print("\nYou can now run the system with:")
    print("  python main.py --input swiggy.csv")
    print("\nOr test with a small sample:")
    print("  python test_sample.py")

if __name__ == "__main__":
    main()

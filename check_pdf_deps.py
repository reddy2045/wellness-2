import sys
import subprocess

def check_dependencies():
    """Check if all required PDF dependencies are installed"""
    required_packages = ['reportlab', 'xhtml2pdf', 'Pillow']
    
    print("Checking PDF generation dependencies...")
    print("=" * 50)
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            all_installed = False
    
    print("=" * 50)
    
    if not all_installed:
        print("\nMissing dependencies. Installing...")
        try:
            for package in required_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("\n All dependencies installed successfully!")
        except Exception as e:
            print(f"\n Failed to install dependencies: {e}")
            print("\nPlease install manually:")
            print("pip install reportlab xhtml2pdf Pillow")
    else:
        print("\n All dependencies are already installed!")
    
    return all_installed

if __name__ == "__main__":
    check_dependencies()
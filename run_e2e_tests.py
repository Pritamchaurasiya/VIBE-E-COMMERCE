import subprocess
import sys
import os

def main():
    print("Preparing to run E2E tests...")

    # Check if frontend is running
    # This is a simplified check. In a real CI, we would start the servers.

    print("Running E2E Suite...")
    env = os.environ.copy()
    env["BASE_URL"] = "http://localhost:3000" # Default

    # Run the playwright script
    try:
        result = subprocess.run(
            [sys.executable, "tests/e2e/e2e_suite.py"],
            env=env,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("Tests Failed.")
            sys.exit(1)
        else:
            print("Tests Passed.")
            sys.exit(0)

    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


import os


files_to_clean = [
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\add_images_script.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\bulk_image_populate.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\check_coverage.py",
    r"c:\IIT MADRAS AI\\VIBE-E-COMMERCE\deploy_enhanced_tracking.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\download_batch_2.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\download_batch_3.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\download_more_images.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\enhance_data.py",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\SECURITY_AUDIT_REPORT.md",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\SECURITY_ENHANCEMENT_GUIDE.md",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\QUICK_START_IMAGES.md",
    r"c:\IIT MADRAS AI\VIBE-E-COMMERCE\static\css\custom.css",
]

for file_path in files_to_clean:
    try:
        # Normalize path
        file_path = os.path.normpath(file_path)
        
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (not found)")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = [line.rstrip() + '\n' for line in lines]
        
        # Remove blank lines at EOF
        while new_lines and new_lines[-1].strip() == '':
            new_lines.pop()
        # Ensure single newline at EOF
        if new_lines and not new_lines[-1].endswith('\n'):
             new_lines[-1] += '\n'
             
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        print(f"Cleaned whitespace in {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

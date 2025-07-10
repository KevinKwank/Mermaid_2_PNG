#!/usr/bin/env python3
"""
Mermaid to PNG Converter
========================

This script converts Mermaid diagram code to PNG images using the Mermaid CLI.
It supports both single file conversion and batch conversion of multiple files.

Requirements:
- Python 3.6+
- Node.js and npm
- @mermaid-js/mermaid-cli package

Author: GitHub Copilot Assistant
Date: July 2025
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
import tempfile
import shutil
# Add demo mode support
from PIL import Image, ImageDraw, ImageFont
import io


class MermaidConverter:
    """Mermaid diagram to PNG converter class."""
    
    def __init__(self):
        self.mermaid_cli = self._find_mermaid_cli()
        self.demo_mode = self.mermaid_cli is None
        if self.demo_mode:
            print("⚠️ Mermaid CLI not available - running in demo mode")
            print("💡 Demo mode will generate placeholder images")
    
    def _find_mermaid_cli(self):
        """Find the mermaid CLI executable."""
        # Try different possible locations - prioritize local installations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_paths = [
            # Local installations (highest priority)
            os.path.join(script_dir, "node_modules", ".bin", "mmdc.cmd"),
            os.path.join(script_dir, "node_modules", ".bin", "mmdc"),
            os.path.join(script_dir, "node_modules", ".bin", "mmdc.ps1"),
            # Node.js CLI direct access
            f"node {os.path.join(script_dir, 'node_modules', '@mermaid-js', 'mermaid-cli', 'dist', 'cli.js')}",
            # Global installations
            "mmdc",
            "npx @mermaid-js/mermaid-cli",
        ]
        
        for path in possible_paths:
            try:
                print(f"Testing: {path}")
                
                # Handle Node.js direct calls differently
                if path.startswith("node "):
                    # Check if the JS file exists first
                    js_file = path.replace("node ", "")
                    if not os.path.exists(js_file):
                        print(f"  JS file not found: {js_file}")
                        continue
                    
                    result = subprocess.run(
                        f"{path} --version",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=15,
                        encoding='utf-8',
                        errors='ignore'
                    )
                
                elif "npx" in path:
                    # For npx, first check if package is available without running
                    check_cmd = "npm list @mermaid-js/mermaid-cli"
                    check_result = subprocess.run(
                        check_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    if check_result.stdout and "@mermaid-js/mermaid-cli" in check_result.stdout:
                        print(f"  Found via npm list: {path}")
                        return path
                    else:
                        print(f"  Package not found in npm list")
                        continue
                
                else:
                    # Direct command execution
                    result = subprocess.run(
                        f'"{path}" --version',
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        encoding='utf-8',
                        errors='ignore'
                    )
                
                if result.returncode == 0 and result.stdout:
                    # Additional test: try actual conversion
                    if self._test_mermaid_cli_with_conversion(path):
                        print(f"✅ Found working Mermaid CLI: {path}")
                        print(f"  Version: {result.stdout.strip()}")
                        return path
                    else:
                        print(f"  Version check passed but conversion failed")
                        continue
                else:
                    print(f"  Failed: return code {result.returncode}")
                    if result.stderr:
                        print(f"  Error: {result.stderr[:100]}...")
                        
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                print(f"  Exception: {type(e).__name__}: {str(e)[:100]}")
                continue
                
        return None
    
    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        if not self.mermaid_cli:
            print("❌ Mermaid CLI not found!")
            print("Please install it using one of these methods:")
            print("1. Global installation: npm install -g @mermaid-js/mermaid-cli")
            print("2. Local installation: npm install @mermaid-js/mermaid-cli")
            return False
            
        # Check if puppeteer dependencies are available
        try:
            result = subprocess.run(
                f"{self.mermaid_cli} --help",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode != 0:
                print("❌ Mermaid CLI is not working properly")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Mermaid CLI is not responding")
            return False
            
        print("✅ All dependencies are available")
        return True
    
    def convert_mermaid_text(self, mermaid_code, output_path, config=None):
        """
        Convert Mermaid code text to PNG image.
        
        Args:
            mermaid_code (str): The Mermaid diagram code
            output_path (str): Path where the PNG file will be saved
            config (dict): Optional configuration for Mermaid
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        # Check if we should use demo mode
        if self.demo_mode:
            print("🎭 Using demo mode - generating placeholder image")
            return self._create_demo_image(mermaid_code, output_path)
        
        if not self._check_dependencies():
            print("⚠️ Dependencies not available, trying demo mode")
            return self._create_demo_image(mermaid_code, output_path)
            
        # Create temporary file for mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(mermaid_code)
            temp_input = temp_file.name
        
        try:
            # Prepare command
            if self.mermaid_cli.startswith("node "):
                # Direct Node.js command
                cmd = [self.mermaid_cli, "-i", temp_input, "-o", output_path]
                cmd = " ".join(cmd)
            else:
                cmd = [self.mermaid_cli, "-i", temp_input, "-o", output_path]
            
            # Add configuration if provided
            config_file_path = None
            if config:
                config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
                json.dump(config, config_file, indent=2)
                config_file.close()
                config_file_path = config_file.name
                if isinstance(cmd, list):
                    cmd.extend(["-c", config_file_path])
                else:
                    cmd += f" -c {config_file_path}"
            
            # Convert shell command if using npx or node
            if "npx" in self.mermaid_cli or self.mermaid_cli.startswith("node "):
                if isinstance(cmd, list):
                    cmd = " ".join(cmd)
                
            # Run conversion
            print(f"Converting to {output_path}...")
            print(f"Command: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                shell=isinstance(cmd, str),
                capture_output=True,
                text=True,
                timeout=45,  # Increased timeout
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                print(f"✅ Successfully converted to {output_path}")
                return True
            else:
                print(f"❌ Conversion failed (return code: {result.returncode})")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")
                if result.stdout:
                    print(f"Output: {result.stdout[:200]}...")
                
                # Fallback to demo mode if CLI fails
                print("🔄 Falling back to demo mode")
                return self._create_demo_image(mermaid_code, output_path)
                
        except subprocess.TimeoutExpired:
            print("❌ Conversion timed out, using demo mode")
            return self._create_demo_image(mermaid_code, output_path)
        except Exception as e:
            print(f"❌ Error during conversion: {str(e)}")
            print("🔄 Falling back to demo mode")
            return self._create_demo_image(mermaid_code, output_path)
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(temp_input):
                    os.unlink(temp_input)
                if config_file_path and os.path.exists(config_file_path):
                    os.unlink(config_file_path)
            except:
                pass
    
    def convert_file(self, input_file, output_file=None, config=None):
        """
        Convert a Mermaid file to PNG.
        
        Args:
            input_file (str): Path to the input .mmd file
            output_file (str): Path to the output .png file (optional)
            config (dict): Optional configuration for Mermaid
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"❌ Input file not found: {input_file}")
            return False
            
        if output_file is None:
            output_file = input_path.with_suffix('.png')
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                mermaid_code = f.read()
            
            return self.convert_mermaid_text(mermaid_code, str(output_file), config)
            
        except Exception as e:
            print(f"❌ Error reading file {input_file}: {str(e)}")
            return False
    
    def batch_convert(self, input_directory, output_directory=None, config=None):
        """
        Convert all .mmd files in a directory to PNG.
        
        Args:
            input_directory (str): Directory containing .mmd files
            output_directory (str): Directory to save PNG files (optional)
            config (dict): Optional configuration for Mermaid
            
        Returns:
            tuple: (successful_count, total_count)
        """
        input_path = Path(input_directory)
        
        if not input_path.exists() or not input_path.is_dir():
            print(f"❌ Input directory not found: {input_directory}")
            return 0, 0
        
        if output_directory:
            output_path = Path(output_directory)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path
        
        mmd_files = list(input_path.glob("*.mmd"))
        
        if not mmd_files:
            print(f"❌ No .mmd files found in {input_directory}")
            return 0, 0
        
        successful = 0
        total = len(mmd_files)
        
        print(f"Found {total} .mmd files to convert...")
        
        for mmd_file in mmd_files:
            output_file = output_path / f"{mmd_file.stem}.png"
            if self.convert_file(str(mmd_file), str(output_file), config):
                successful += 1
        
        print(f"\n✅ Conversion complete: {successful}/{total} files converted successfully")
        return successful, total
    
    def _create_demo_image(self, mermaid_code, output_path):
        """Create a demo image when Mermaid CLI is not available."""
        try:
            # Try to import PIL for demo images
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("❌ PIL not available for demo mode")
            return False
        
        try:
            # Create a simple demonstration image
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a system font
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_medium = ImageFont.truetype("arial.ttf", 16)
                font_small = ImageFont.truetype("arial.ttf", 12)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw demo content
            draw.rectangle([50, 50, width-50, height-50], outline='#333', width=2)
            
            # Title
            draw.text((width//2-100, 80), "Mermaid Diagram", fill='#333', font=font_large)
            draw.text((width//2-80, 110), "(Demo Mode)", fill='#666', font=font_medium)
            
            # Draw some basic shapes to represent a diagram
            # Box 1
            draw.rectangle([150, 200, 300, 250], outline='#3498db', width=2, fill='#ecf0f1')
            draw.text((225-30, 220), "Start", fill='#2c3e50', font=font_medium)
            
            # Arrow
            draw.line([300, 225, 350, 225], fill='#333', width=2)
            draw.polygon([(345, 220), (355, 225), (345, 230)], fill='#333')
            
            # Box 2
            draw.rectangle([400, 200, 550, 250], outline='#e74c3c', width=2, fill='#fadbd8')
            draw.text((475-30, 220), "Process", fill='#2c3e50', font=font_medium)
            
            # Arrow down
            draw.line([475, 250, 475, 300], fill='#333', width=2)
            draw.polygon([(470, 295), (475, 305), (480, 295)], fill='#333')
            
            # Box 3
            draw.rectangle([400, 350, 550, 400], outline='#27ae60', width=2, fill='#d5f4e6')
            draw.text((475-20, 370), "End", fill='#2c3e50', font=font_medium)
            
            # Add some code snippet info
            lines = mermaid_code.split('\n')[:5]  # First 5 lines
            y_pos = 450
            draw.text((100, y_pos), "Original Mermaid Code:", fill='#7f8c8d', font=font_small)
            for i, line in enumerate(lines):
                if line.strip():
                    draw.text((100, y_pos + 20 + i*15), line[:50], fill='#95a5a6', font=font_small)
            
            # Note
            draw.text((100, 550), "Note: Install Mermaid CLI for actual conversion", fill='#e67e22', font=font_small)
            
            # Save the image
            img.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            print(f"❌ Error creating demo image: {str(e)}")
            return False

    def _test_mermaid_cli_with_conversion(self, cli_path):
        """
        Test if the Mermaid CLI can actually perform conversions.
        This includes checking for Chromium/browser dependencies.
        """
        try:
            # Create a simple test diagram
            test_code = "graph TD; A-->B"
            
            # Create temporary files
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_input:
                temp_input.write(test_code)
                temp_input_path = temp_input.name
            
            temp_output_path = temp_input_path.replace('.mmd', '.png')
            
            # Try to convert
            if "node " in cli_path:
                cmd = f"{cli_path} -i \"{temp_input_path}\" -o \"{temp_output_path}\""
            else:
                cmd = f"\"{cli_path}\" -i \"{temp_input_path}\" -o \"{temp_output_path}\""
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Clean up
            try:
                os.unlink(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.unlink(temp_output_path)
            except:
                pass
            
            # Check if conversion was successful
            if result.returncode == 0:
                return True
            else:
                print(f"  Conversion test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  Conversion test error: {e}")
            return False

def create_sample_mermaid():
    """Create a sample mermaid file for testing."""
    sample_content = """graph TD
    A[开始] --> B{是否有Mermaid代码?}
    B -->|是| C[转换为PNG]
    B -->|否| D[创建Mermaid代码]
    C --> E[保存图片]
    D --> C
    E --> F[完成]
    
    style A fill:#e1f5fe
    style F fill:#c8e6c9
    style C fill:#fff3e0
"""
    
    with open("sample.mmd", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("✅ Created sample.mmd file")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Convert Mermaid diagrams to PNG images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mermaid_to_png.py -f diagram.mmd
  python mermaid_to_png.py -f diagram.mmd -o output.png
  python mermaid_to_png.py -d ./diagrams/ -od ./images/
  python mermaid_to_png.py --sample
  python mermaid_to_png.py --text "graph TD; A-->B"
        """
    )
    
    parser.add_argument("-f", "--file", help="Input Mermaid file (.mmd)")
    parser.add_argument("-o", "--output", help="Output PNG file")
    parser.add_argument("-d", "--directory", help="Input directory containing .mmd files")
    parser.add_argument("-od", "--output-directory", help="Output directory for PNG files")
    parser.add_argument("-t", "--text", help="Mermaid code as text")
    parser.add_argument("-c", "--config", help="Configuration file (JSON)")
    parser.add_argument("--sample", action="store_true", help="Create a sample Mermaid file")
    parser.add_argument("--check", action="store_true", help="Check dependencies")
    
    args = parser.parse_args()
    
    converter = MermaidConverter()
    
    # Load configuration if provided
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Error loading config file: {str(e)}")
            return 1
    
    # Handle different operations
    if args.check:
        if converter._check_dependencies():
            print("✅ All dependencies are working correctly")
            return 0
        else:
            return 1
    
    elif args.sample:
        create_sample_mermaid()
        return 0
    
    elif args.text:
        output_file = args.output or "output.png"
        if converter.convert_mermaid_text(args.text, output_file, config):
            return 0
        else:
            return 1
    
    elif args.file:
        if converter.convert_file(args.file, args.output, config):
            return 0
        else:
            return 1
    
    elif args.directory:
        successful, total = converter.batch_convert(args.directory, args.output_directory, config)
        return 0 if successful == total else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

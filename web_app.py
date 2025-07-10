#!/usr/bin/env python3
"""
Mermaid to PNG Web API
=====================

Flask web API for the Mermaid to PNG converter.
Provides REST endpoints for converting Mermaid diagrams to PNG images.

Author: Kevin KWAN
Date: July 2025
"""

import os
import json
import base64
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from mermaid_to_png import MermaidConverter
import io

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize converter
converter = MermaidConverter()


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'mermaid_cli_available': converter.mermaid_cli is not None
    })


@app.route('/api/check-dependencies')
def check_dependencies():
    """Check if all dependencies are available."""
    is_available = converter._check_dependencies()
    return jsonify({
        'dependencies_ok': is_available,
        'mermaid_cli': converter.mermaid_cli
    })


@app.route('/api/convert', methods=['POST'])
def convert_mermaid():
    """
    Convert Mermaid code to PNG.
    
    Expected JSON payload:
    {
        "mermaid_code": "graph TD; A-->B",
        "config": {...},  // optional
        "filename": "diagram.png"  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'mermaid_code' not in data:
            return jsonify({'error': 'Missing mermaid_code in request'}), 400
        
        mermaid_code = data['mermaid_code']
        config = data.get('config', None)
        filename = secure_filename(data.get('filename', 'diagram.png'))
        
        if not filename.endswith('.png'):
            filename += '.png'
        
        # Create output file path
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Convert the Mermaid code
        success = converter.convert_mermaid_text(mermaid_code, output_path, config)
        
        if success and os.path.exists(output_path):
            # Read the generated PNG file and encode as base64
            with open(output_path, 'rb') as f:
                png_data = f.read()
                png_base64 = base64.b64encode(png_data).decode('utf-8')
            
            # Clean up the file
            os.remove(output_path)
            
            return jsonify({
                'success': True,
                'image_data': png_base64,
                'filename': filename,
                'message': 'Conversion successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversion failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/convert-file', methods=['POST'])
def convert_file():
    """
    Convert uploaded Mermaid file to PNG.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.mmd'):
            return jsonify({'error': 'File must have .mmd extension'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Prepare output filename
        output_filename = filename.replace('.mmd', '.png')
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Get optional config
        config = None
        if 'config' in request.form:
            try:
                config = json.loads(request.form['config'])
            except json.JSONDecodeError:
                pass
        
        # Convert the file
        success = converter.convert_file(input_path, output_path, config)
        
        if success and os.path.exists(output_path):
            # Read the generated PNG file and encode as base64
            with open(output_path, 'rb') as f:
                png_data = f.read()
                png_base64 = base64.b64encode(png_data).decode('utf-8')
            
            # Clean up files
            os.remove(input_path)
            os.remove(output_path)
            
            return jsonify({
                'success': True,
                'image_data': png_base64,
                'filename': output_filename,
                'message': 'File conversion successful'
            })
        else:
            # Clean up input file even if conversion failed
            if os.path.exists(input_path):
                os.remove(input_path)
            
            return jsonify({
                'success': False,
                'error': 'File conversion failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/examples')
def get_examples():
    """Get example Mermaid diagrams."""
    examples = {
        'flowchart': {
            'name': '流程图',
            'code': '''graph TD
    A[开始] --> B{条件判断}
    B -->|是| C[执行操作]
    B -->|否| D[其他操作]
    C --> E[结束]
    D --> E
    
    style A fill:#e1f5fe
    style E fill:#c8e6c9
    style C fill:#fff3e0'''
        },
        'sequence': {
            'name': '序列图',
            'code': '''sequenceDiagram
    participant 用户
    participant 系统
    participant 数据库
    
    用户->>系统: 发送请求
    系统->>数据库: 查询数据
    数据库-->>系统: 返回结果
    系统-->>用户: 响应结果'''
        },
        'class': {
            'name': '类图',
            'code': '''classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    
    class Dog {
        +String breed
        +bark()
    }
    
    class Cat {
        +boolean indoor
        +meow()
    }
    
    Animal <|-- Dog
    Animal <|-- Cat'''
        },
        'pie': {
            'name': '饼图',
            'code': '''pie title 编程语言使用统计
    "Python" : 35
    "JavaScript" : 25
    "Java" : 20
    "C++" : 12
    "其他" : 8'''
        },
        'gitgraph': {
            'name': 'Git图',
            'code': '''gitgraph
    commit id: "初始提交"
    branch develop
    checkout develop
    commit id: "添加功能A"
    commit id: "修复bug"
    checkout main
    merge develop
    commit id: "发布v1.0"'''
        }
    }
    
    return jsonify(examples)


if __name__ == '__main__':
    # Check dependencies on startup
    if not converter._check_dependencies():
        print("⚠️ Warning: Mermaid CLI dependencies not available")
        print("Some features may not work properly")
    
    print("🚀 Starting Mermaid to PNG Web Server...")
    print("📱 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

import os
from flask import Flask, request, jsonify, send_file, render_template, session, after_this_request
from werkzeug.utils import secure_filename
from scapy.all import *
import random
import socket
from collections import Counter
import dns.resolver
import shutil
import pyshark

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'  # Required for session

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def cleanup_files():
    """Clean up temporary files"""
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        print(f"Error cleaning up files: {str(e)}")

def get_dns_record(ip):
    """Get DNS record for an IP address"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None

def analyze_pcap(file_path):
    """Analyze PCAP file and return top talkers"""
    packets = rdpcap(file_path)
    ip_counter = Counter()
    
    # Count IP addresses
    for packet in packets:
        if IP in packet:
            ip_counter[packet[IP].src] += 1
            ip_counter[packet[IP].dst] += 1
    
    # Get top 10 IPs
    top_ips = ip_counter.most_common(10)
    
    # Get DNS records for top IPs
    results = []
    for ip, count in top_ips:
        dns_record = get_dns_record(ip)
        results.append({
            'ip': ip,
            'dns': dns_record,
            'count': count
        })
    
    return results

def modify_pcap(original_file, modified_file, modifications):
    """Modify IP addresses in a PCAP file"""
    try:
        # Create a dictionary of IP modifications for quick lookup
        ip_modifications = {m['original_ip']: m['new_ip'] for m in modifications if m['new_ip']}
        
        # Read the original PCAP file
        packets = rdpcap(original_file)
        modified_packets = []
        
        for packet in packets:
            try:
                if IP in packet:
                    # Modify source IP if needed
                    if packet[IP].src in ip_modifications:
                        packet[IP].src = ip_modifications[packet[IP].src]
                    
                    # Modify destination IP if needed
                    if packet[IP].dst in ip_modifications:
                        packet[IP].dst = ip_modifications[packet[IP].dst]
                
                modified_packets.append(packet)
            except Exception as e:
                print(f"Error processing packet: {e}")
                modified_packets.append(packet)  # Keep original packet if modification fails
                continue
        
        # Write modified packets to new file
        wrpcap(modified_file, modified_packets)
        
        if not os.path.exists(modified_file):
            raise Exception("Failed to create modified file")
            
    except Exception as e:
        raise Exception(f"Error modifying PCAP file: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    if not file.filename.endswith('.pcap'):
        return jsonify({'success': False, 'message': 'Please upload a .pcap file'})
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Store the file path in session for later use
        session['original_file'] = file_path
        
        # Analyze the PCAP file
        top_talkers = analyze_pcap(file_path)
        
        return jsonify({
            'success': True,
            'top_talkers': top_talkers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing file: {str(e)}'
        })

@app.route('/modify', methods=['POST'])
def modify():
    if 'original_file' not in session:
        return jsonify({'success': False, 'message': 'No file found in session'})
    
    try:
        data = request.get_json()
        modifications = data.get('modifications', [])
        
        if not modifications:
            return jsonify({'success': False, 'message': 'No modifications provided'})
        
        # Get the original file path
        original_file = session['original_file']
        if not os.path.exists(original_file):
            return jsonify({'success': False, 'message': 'Original file not found'})
        
        # Create a new file path for the modified PCAP
        modified_file = os.path.join(app.config['UPLOAD_FOLDER'], 'modified_' + os.path.basename(original_file))
        
        # Apply modifications
        modify_pcap(original_file, modified_file, modifications)
        
        # Verify the modified file exists
        if not os.path.exists(modified_file):
            return jsonify({'success': False, 'message': 'Failed to create modified file'})
        
        # Store the modified file path in session
        session['modified_file'] = modified_file
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download')
def download_page():
    return render_template('download.html')

@app.route('/download_file')
def download_file():
    modified_file = session.get('modified_file')
    if not modified_file or not os.path.exists(modified_file):
        return jsonify({'success': False, 'message': 'No modified file available'})
    
    try:
        @after_this_request
        def cleanup(response):
            try:
                # Clean up both original and modified files
                if 'original_file' in session:
                    if os.path.exists(session['original_file']):
                        os.remove(session['original_file'])
                if 'modified_file' in session:
                    if os.path.exists(session['modified_file']):
                        os.remove(session['modified_file'])
                # Clear session
                session.clear()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")
            return response

        return send_file(
            modified_file,
            as_attachment=True,
            download_name='modified_' + os.path.basename(modified_file)
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Clean up any existing files before starting
    cleanup_files()
    # Ensure we're binding to all interfaces
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
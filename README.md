# PCAP Anonymizer 🔒🌐

A web-based tool for anonymizing IP addresses in PCAP files. This tool allows you to upload a PCAP file, modify IP addresses, and download the modified version while preserving the original DNS records.

## 🛠 Features

- Upload PCAP files 📁
- View top talkers (IP addresses and their DNS records)
- Modify IP addresses 🔐
- Download modified PCAP files 🌐
- Clean and simple web interface
- Docker containerization for easy deployment

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/shervinhariri/pcap-anonymizer.git
cd pcap-anonymizer
```

2. Build and run the Docker container:
```bash
docker build -t pcap-anonymizer .
docker run -d -p 5001:5001 --name pcap-anonymizer pcap-anonymizer
```

3. Access the application at: [http://localhost:5001/](http://localhost:5001/)

## 📖 How to Use

### Step 1: Upload a PCAP File
- Open your web browser and navigate to `http://localhost:5001`
- Click the "Choose File" button
- Select your PCAP file
- Click "Upload PCAP File"
- The system will analyze the file and display the top talkers

### Step 2: Modify IP Addresses
- In the results table, you'll see:
  - IP addresses
  - Associated DNS records
  - Packet counts
- Click the "Modify IPs and DNS Records" button
- For each IP you want to modify:
  - Enter the new IP address in the "New IP" field
  - Leave the DNS record field unchanged (DNS records are preserved)
- Click "Apply Changes and Generate Modified PCAP"

### Step 3: Download the Modified PCAP
- After successful modification, you'll be redirected to the download page
- Click the "Download Modified PCAP" button
- The modified PCAP file will be downloaded to your machine
- The file will be named `modified_[original_filename].pcap`

## ⚙️ Technology Stack

- **Backend**: Python/Flask
- **Frontend**: Modern HTML/CSS
- **PCAP Processing**: Scapy
- **Containerization**: Docker

## 📝 Important Notes

- The tool only modifies IP addresses, not DNS records
- Original DNS records are preserved in the modified PCAP
- Maximum file size is 16MB
- Temporary files are automatically cleaned up after download
- The container runs on port 5001

## 🔧 Troubleshooting

If you encounter any issues:

1. Check if the container is running:
```bash
docker ps | grep pcap-anonymizer
```

2. View container logs:
```bash
docker logs pcap-anonymizer
```

3. Restart the container if needed:
```bash
docker stop pcap-anonymizer
docker rm pcap-anonymizer
docker run -d -p 5001:5001 --name pcap-anonymizer pcap-anonymizer
```

## 🚀 Future Enhancements

- Launch a public website for direct PCAP anonymization
- Add user authentication
- Enable batch processing of multiple PCAP files
- Enhance UI/UX
- Add more customization options for IP address modification

## 🤝 Contributing

Feel free to open an issue or submit a pull request to contribute to the project! We're always open to suggestions and improvements.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

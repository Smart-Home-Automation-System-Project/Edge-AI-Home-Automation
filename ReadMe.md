# IoT-Based-Smart-Home-Automation-System

## Edge AI Home Automation

### Project Setup Instructions

#### Prerequisites

Before setting up the project, make sure you have the following:

- **Python 3.11.8** installed
- **TensorFlow 2.16.1** installed

You can install Python from the official website: [Python Downloads](https://www.python.org/downloads/)  
To install TensorFlow, use the following command:

```bash
pip install tensorflow==2.16.1
```

#### Setting up the Environment Variables

1. **Create a .env file**:
   In your project directory, create a new file named .env.

2. **Edit the .env file**:
   Inside your .env file, add your AWS credentials. Here's an example:
   ```
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=us-east-1
   ```
   Replace your_aws_access_key_id and your_aws_secret_access_key with your actual AWS credentials.

3. **Save the .env file**.

#### Installing Dependencies

Once your .env file is set up, install the required dependencies for the project. You can use the following commands to install the necessary packages:

1. **Create a virtual environment**: 
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux: (didn't check)
   ```bash
   source venv/bin/activate
   ```

3. **Install the required Python packages**:
   ```bash
   pip install boto3 python-dotenv
   ```

#### Updating File Paths

Make sure to replace any hardcoded file paths in the code with paths specific to your local environment.

For example, replace paths in download.py, upload.py, and other scripts where paths are hardcoded.

#### Running the Project

1. **Upload a file**:
   To upload a CSV file to S3 using the upload.py script, run the following command:
   ```bash
   python upload.py
   ```

2. **Download a model**:
   To download the latest model from S3 using the download.py script, run:
   ```bash
   python download.py
   ```

3. **Predict using the model**:
   Once the model is downloaded and extracted (which happens automatically), you can run the predict.py script to make predictions:
   ```bash
   python predict.py
   ```
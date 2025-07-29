#!/usr/bin/env python3
"""
Manual File Processing
Manually process the uploaded Excel file
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv('/home/david/mockDataRepo/mockDataRepo/backend/.env')

sys.path.append('/home/david/mockDataRepo/mockDataRepo/backend')

from app.services.cleaning_service import CleaningService
from app.services.db_service import DatabaseService

async def manual_process():
    """Manually process the uploaded file"""
    
    upload_id = '8affd23c-38da-4b5c-bc4a-7a07fce8b9fd'
    filename = 'mock_data_100_rows .xlsx'  # Note the space in filename
    user_id = 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d'
    
    # Read the uploaded file
    file_path = f'/home/david/mockDataRepo/mockDataRepo/backend/uploads/{upload_id}_{filename}'
    
    try:
        with open(file_path, 'rb') as f:
            file_contents = f.read()
        
        print(f"📁 File read successfully: {len(file_contents)} bytes")
        
        # Create cleaning service
        cleaning_service = CleaningService()
        
        # Process the file
        print(f"🔄 Starting manual processing...")
        await cleaning_service.process_file(upload_id, filename, file_contents, user_id)
        
        print(f"✅ Manual processing completed!")
        
    except Exception as e:
        print(f"❌ Error during manual processing: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(manual_process())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Performance test script for optimized pandas operations
"""

import asyncio
import time
import pandas as pd
import numpy as np
from app.pipeline.normalizers import DataNormalizer
from app.pipeline.cleaners import DataCleaner
from app.services.db_service import DatabaseService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sample_data(rows: int = 10000) -> pd.DataFrame:
    """Generate sample DataFrame for testing"""
    np.random.seed(42)
    
    data = {
        'ean': [f"123456789012{i:01d}" for i in range(rows)],
        'quantity': np.random.randint(1, 100, rows),
        'sales_eur': np.random.uniform(10, 1000, rows),
        'year': np.random.choice([2023, 2024, 2025], rows),
        'month': np.random.randint(1, 13, rows),
        'functional_name': [f"Product {i}" for i in range(rows)],
        'reseller': np.random.choice(['TestReseller1', 'TestReseller2'], rows),
        'currency': 'EUR'
    }
    
    return pd.DataFrame(data)

async def test_normalization_performance():
    """Test the performance of the optimized normalization"""
    logger.info("=== Testing Normalization Performance ===")
    
    # Test with different data sizes
    test_sizes = [1000, 5000, 15000]  # 15k will trigger chunked processing
    normalizer = DataNormalizer()
    
    for size in test_sizes:
        logger.info(f"\nTesting normalization with {size} rows...")
        df = generate_sample_data(size)
        
        start_time = time.time()
        normalized_df = await normalizer.normalize_data(df, "skins_nl")
        end_time = time.time()
        
        processing_time = end_time - start_time
        rows_per_second = size / processing_time if processing_time > 0 else 0
        
        logger.info(f"  Size: {size} rows")
        logger.info(f"  Time: {processing_time:.3f} seconds")
        logger.info(f"  Rate: {rows_per_second:.0f} rows/second")
        logger.info(f"  Output rows: {len(normalized_df)}")
        logger.info(f"  Memory efficiency: {'Chunked processing' if size > 10000 else 'Standard processing'}")

async def test_cleaning_performance():
    """Test the performance of the optimized cleaning"""
    logger.info("\n=== Testing Cleaning Performance ===")
    
    # Test with different data sizes
    test_sizes = [1000, 10000, 60000]  # 60k will trigger chunked processing
    cleaner = DataCleaner()
    
    for size in test_sizes:
        logger.info(f"\nTesting cleaning with {size} rows...")
        df = generate_sample_data(size)
        
        start_time = time.time()
        cleaned_df, transformations = await cleaner.clean_data(df, "skins_nl")
        end_time = time.time()
        
        processing_time = end_time - start_time
        rows_per_second = size / processing_time if processing_time > 0 else 0
        
        logger.info(f"  Size: {size} rows")
        logger.info(f"  Time: {processing_time:.3f} seconds")
        logger.info(f"  Rate: {rows_per_second:.0f} rows/second")
        logger.info(f"  Output rows: {len(cleaned_df)}")
        logger.info(f"  Transformations: {len(transformations)}")
        logger.info(f"  Processing type: {'Chunked' if size > 50000 else 'Standard'}")

async def test_database_performance():
    """Test the performance of the optimized database operations"""
    logger.info("\n=== Testing Database Performance ===")
    
    # Test with different data sizes
    test_sizes = [1000, 3000, 8000]  # 8k will trigger chunked processing
    db_service = DatabaseService()
    
    for size in test_sizes:
        logger.info(f"\nTesting database insertion with {size} entries...")
        
        # Generate sample entries
        entries = []
        for i in range(size):
            entries.append({
                'product_ean': f"123456789012{i:01d}",
                'quantity': i + 1,
                'sales_eur': 100.0 + i,
                'year': 2024,
                'month': 6,
                'functional_name': f"Product {i}",
                'reseller': 'TestReseller',
                'currency': 'EUR'
            })
        
        upload_id = f"test_upload_{size}_{int(time.time())}"
        
        start_time = time.time()
        await db_service.insert_mock_data(upload_id, entries)
        end_time = time.time()
        
        processing_time = end_time - start_time
        entries_per_second = size / processing_time if processing_time > 0 else 0
        
        logger.info(f"  Size: {size} entries")
        logger.info(f"  Time: {processing_time:.3f} seconds")
        logger.info(f"  Rate: {entries_per_second:.0f} entries/second")
        logger.info(f"  Processing type: {'Chunked' if size > 5000 else 'Standard'}")

async def test_end_to_end_pipeline():
    """Test the complete optimized pipeline"""
    logger.info("\n=== Testing End-to-End Pipeline Performance ===")
    
    # Test with medium-large dataset
    size = 25000  # This will trigger chunked processing in multiple components
    logger.info(f"Testing complete pipeline with {size} rows...")
    
    # Generate data
    df = generate_sample_data(size)
    logger.info(f"Generated {len(df)} rows of test data")
    
    # Initialize components
    cleaner = DataCleaner()
    normalizer = DataNormalizer()
    db_service = DatabaseService()
    
    # Track total time
    pipeline_start = time.time()
    
    # Step 1: Cleaning
    clean_start = time.time()
    cleaned_df, transformations = await cleaner.clean_data(df, "skins_nl")
    clean_end = time.time()
    logger.info(f"Cleaning: {clean_end - clean_start:.3f}s ({len(cleaned_df)} rows output)")
    
    # Step 2: Normalization
    norm_start = time.time()
    normalized_df = await normalizer.normalize_data(cleaned_df, "skins_nl")
    norm_end = time.time()
    logger.info(f"Normalization: {norm_end - norm_start:.3f}s ({len(normalized_df)} rows output)")
    
    # Step 3: Database conversion and insertion
    db_start = time.time()
    entries = normalized_df.to_dict('records')
    upload_id = f"pipeline_test_{int(time.time())}"
    await db_service.insert_mock_data(upload_id, entries)
    db_end = time.time()
    logger.info(f"Database operations: {db_end - db_start:.3f}s ({len(entries)} entries)")
    
    # Total pipeline performance
    pipeline_end = time.time()
    total_time = pipeline_end - pipeline_start
    throughput = size / total_time
    
    logger.info(f"\n--- Pipeline Summary ---")
    logger.info(f"Total processing time: {total_time:.3f} seconds")
    logger.info(f"Overall throughput: {throughput:.0f} rows/second")
    logger.info(f"Input rows: {size}")
    logger.info(f"Output entries: {len(entries)}")
    logger.info(f"Efficiency: {(len(entries) / size) * 100:.1f}% data retention")

async def main():
    """Run all performance tests"""
    logger.info("Starting pandas optimization performance tests...")
    logger.info("=" * 60)
    
    try:
        await test_normalization_performance()
        await test_cleaning_performance()  
        await test_database_performance()
        await test_end_to_end_pipeline()
        
        logger.info("\n" + "=" * 60)
        logger.info("Performance testing completed successfully!")
        logger.info("\nKey optimizations:")
        logger.info("✅ Async/await patterns prevent event loop blocking")
        logger.info("✅ Chunked processing handles large datasets efficiently")
        logger.info("✅ Thread pool execution for CPU-intensive operations")
        logger.info("✅ Vectorized pandas operations for better performance")
        logger.info("✅ Memory-efficient data type conversions")
        
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
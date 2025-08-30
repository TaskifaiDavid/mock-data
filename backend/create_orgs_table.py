#!/usr/bin/env python3
"""
Quick script to create the organizations table for demo.
"""
import asyncio
import asyncpg
from app.utils.config import get_settings

async def create_organizations_table():
    settings = get_settings()
    
    # Extract connection details from DATABASE_URL
    db_url = settings.database_url
    print(f"Connecting to database...")
    
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(db_url)
        
        # Create organizations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS public.organizations (
                id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
                name text NOT NULL UNIQUE,
                slug text NOT NULL UNIQUE,
                settings jsonb DEFAULT '{}',
                is_active boolean DEFAULT true,
                created_at timestamp with time zone DEFAULT now(),
                updated_at timestamp with time zone DEFAULT now()
            );
        """)
        print("✓ Organizations table created")
        
        # Create index
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_organizations_slug 
            ON public.organizations(slug) WHERE is_active = true;
        """)
        print("✓ Organizations index created")
        
        # Insert default organization
        await conn.execute("""
            INSERT INTO public.organizations (id, name, slug, settings) 
            VALUES ($1, $2, $3, $4) 
            ON CONFLICT (name) DO NOTHING;
        """, 
        '00000000-0000-0000-0000-000000000001',
        'Default Organization', 
        'default-org',
        {'created_by_migration': True, 'phase': 'phase_1'}
        )
        print("✓ Default organization created")
        
        # Verify the table exists
        result = await conn.fetch("SELECT * FROM public.organizations WHERE slug = 'default-org'")
        print(f"✓ Verification: Found {len(result)} default organization(s)")
        
        await conn.close()
        print("✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_organizations_table())
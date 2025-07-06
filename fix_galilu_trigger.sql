-- Drop the problematic trigger
DROP TRIGGER IF EXISTS galilu_functional_name_trigger ON sellout_entries2;

-- Drop the function as well
DROP FUNCTION IF EXISTS update_galilu_functional_name();

-- Drop the new trigger if it exists from previous run
DROP TRIGGER IF EXISTS galilu_functional_name_mapping_trigger ON sellout_entries2;

-- Create a proper BEFORE INSERT trigger that maps Polish names to functional_name
CREATE OR REPLACE FUNCTION map_galilu_functional_name()
RETURNS TRIGGER AS $$
BEGIN
    -- Only process rows where reseller is 'Galilu'
    IF NEW.reseller = 'Galilu' AND NEW.functional_name IS NOT NULL THEN
        -- Try to find the correct functional_name by looking up the Polish name in galilu_name column
        DECLARE
            mapped_functional_name text;
        BEGIN
            SELECT p.functional_name INTO mapped_functional_name
            FROM products p
            WHERE p.galilu_name = NEW.functional_name
            AND p.galilu_name IS NOT NULL
            LIMIT 1;
            
            -- If we found a mapping, use it; otherwise keep the original
            IF mapped_functional_name IS NOT NULL THEN
                NEW.functional_name := mapped_functional_name;
            END IF;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the BEFORE INSERT trigger
CREATE TRIGGER galilu_functional_name_mapping_trigger
    BEFORE INSERT ON sellout_entries2
    FOR EACH ROW
    EXECUTE FUNCTION map_galilu_functional_name();
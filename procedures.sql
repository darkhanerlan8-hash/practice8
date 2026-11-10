
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM contacts
        WHERE name = p_name
    ) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone)
        VALUES(p_name, p_phone);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    IN p_data JSONB,
    INOUT p_invalid JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    item JSONB;
    n TEXT;
    ph TEXT;
BEGIN
    p_invalid := '[]'::JSONB;

    FOR item IN
        SELECT value
        FROM jsonb_array_elements(p_data)
    LOOP
        n := TRIM(item->>'name');
        ph := TRIM(item->>'phone');

        IF COALESCE(n, '') = ''
           OR COALESCE(ph, '') !~ '^\+?[0-9]{10,15}$'
        THEN
            p_invalid := p_invalid ||
                jsonb_build_array(item);
        ELSE
            CALL upsert_contact(
                n::VARCHAR,
                ph::VARCHAR
            );
        END IF;
    END LOOP;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(
    p_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE (p_name IS NOT NULL AND name = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;

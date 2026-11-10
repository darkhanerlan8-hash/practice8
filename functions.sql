
CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(name VARCHAR, phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.phone
    FROM contacts c
    WHERE c.name ILIKE '%' || p || '%'
       OR c.phone ILIKE '%' || p || '%'
    ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit INT,
    p_offset INT
)
RETURNS TABLE(name VARCHAR, phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.phone
    FROM contacts c
    ORDER BY c.name, c.phone
    LIMIT GREATEST(p_limit, 0)
    OFFSET GREATEST(p_offset, 0);
END;
$$ LANGUAGE plpgsql;

-- Enable plpgsql if not already
CREATE EXTENSION IF NOT EXISTS plpgsql;

-- Function to notify on insert
CREATE OR REPLACE FUNCTION notify_taux_insert() RETURNS trigger AS $$
DECLARE
    payload JSON;
BEGIN
    payload := json_build_object(
        'id', NEW.id,
        'devise_source', NEW.devise_source,
        'devise_cible', NEW.devise_cible,
        'taux', NEW.taux,
        'date_taux', NEW.date_taux
    );

    PERFORM pg_notify('taux_change_channel', payload::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_notify_taux_insert ON taux_de_change;

CREATE TRIGGER trigger_notify_taux_insert
AFTER INSERT ON taux_de_change
FOR EACH ROW EXECUTE FUNCTION notify_taux_insert();
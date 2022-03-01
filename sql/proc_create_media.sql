CREATE OR REPLACE PROCEDURE create_media(
	in _id character(8),
	inout _total integer DEFAULT NULL
)
LANGUAGE plpgsql    
AS $$
BEGIN
	INSERT INTO medias(media_id, media_count)
	VALUES(_id, 1);

	SELECT media_count FROM medias
	WHERE media_id = _id
	INTO _total;

END;$$
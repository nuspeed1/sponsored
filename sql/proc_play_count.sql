CREATE OR REPLACE PROCEDURE play_count(
	_id character(8),
	inout _total int DEFAULT NULL
)
LANGUAGE plpgsql    
AS $$
BEGIN
	UPDATE medias
	SET media_count = media_count + 1
	WHERE media_id = _id;

	SELECT media_count FROM medias
	WHERE media_id = _id
	INTO _total;

END;$$
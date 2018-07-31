CREATE TABLE items (
	item_id		INTEGER 	PRIMARY KEY,
	word		TEXT,
	mean		TEXT,
	level		INTEGER DEFAULT 0
);
CREATE INDEX word_index on items(word);


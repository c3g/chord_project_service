DROP TABLE IF EXISTS projects;

CREATE TABLE projects (
    id TEXT PRIMARY KEY,       -- UUID4
    name TEXT UNIQUE NOT NULL, -- Unique human-readable name
    description TEXT NOT NULL, -- Description of project
    data_use TEXT NOT NULL     -- JSON object for DUO specification (TODO: link to schema)
);

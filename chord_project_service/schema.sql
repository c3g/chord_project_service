DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS project_datasets;

CREATE TABLE projects (
    id TEXT PRIMARY KEY,       -- UUID4
    name TEXT UNIQUE NOT NULL, -- Unique human-readable name
    description TEXT NOT NULL, -- Description of project
    data_use TEXT NOT NULL     -- JSON object for DUO specification (TODO: link to schema)
);

CREATE TABLE project_datasets (
    dataset_id TEXT PRIMARY KEY,                    -- Dataset UUID4
    service_id TEXT NOT NULL,                       -- Service UUID4
    data_type_id TEXT NOT NULL,                     -- Data Type ID
    project_id TEXT NOT NULL,                       -- Project UUID4
    FOREIGN KEY (project_id) REFERENCES projects
);

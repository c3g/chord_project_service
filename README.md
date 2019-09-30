# CHORD Project Service

Project, data use, and dataset ownership management service for the CHORD project.

```json
{
  "id": "project",
  "repository": "https://github.com/c3g/chord_project_service",
  "data_service": false,
  "apt_dependencies": [],
  "wsgi": true,
  "python_module": "chord_project_service.app",
  "python_callable": "application",
  "python_environment": {
    "DATABASE": "{SERVICE_DATA}/project_service.db"
  }
}
```

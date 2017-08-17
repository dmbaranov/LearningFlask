Create .envrc file in the folder with the next content (this is just an example):
```
source env/bin/activate
export APP_SETTINGS="app.config.DevelopmentConfig"
export DATABASE_URL="postgresql://localhost/path-to-database"
export SECRET_KEY="this-is-a-secret-key"
```


Don't forget to use `direnv` to automatically load env variables.
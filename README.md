### How to use this

1. Make spec file
```bash
    ~/Nomad_Distributed pyi-makespec --onefile -icon=app.ico --name=Nomad nomad_dist.py
```

2. Edit the spec file to include Chromedriver
    1. Tuple containing absolute path of Chromedriver, followed by relative path for the script. (Where it is now, where it will be)
    
```python
    binaries=[('C:\\Users\\estasney\\PycharmProjects\\Nomad_Distributed\\chromedriver.exe',
                        '.')],
``` 
   
3. Building .exe
    1. ` pyinstaller --onefile Nomad.spec nomad_dist.py`
    
4. Include a copy of chromedriver.exe in the dist folder
```
\dist
    nomad_dist.exe
    chromedriver.exe
```

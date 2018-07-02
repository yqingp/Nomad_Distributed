### How to use this

1. Make spec files
```bash
    ~/Nomad_Distributed/app_folder/local pyi-makespec --onefile -icon=path/to/icon.ico --name=Nomad_Local nomad_local.py
    ~/Nomad_Distributed/app_folder/distributed pyi-makespec --onefile -icon=path/to/icon.ico --name=Nomad_Distributed nomad_dist.py
```

2. Edit the spec file to include Chromedriver
    1. Tuple containing absolute path of Chromedriver, followed by relative path for the script. (Where it is now, where it will be)
    
```python
binaries=[('C:\\Users\\estasney\\PycharmProjects\\Nomad_Distributed\\app_folder\local\chromedriver.exe',
                        '.')],
```

```python
binaries=[('C:\\Users\\estasney\\PycharmProjects\\Nomad_Distributed\\app_folder\distributed\chromedriver.exe',
                        '.')],
``` 
   
3. Building .exe
    1. ` pyinstaller --onefile Nomad_Local.spec nomad_local.py`
    2. `pyinstaller --onefile Nomad_Distributed.spec nomad_dist.py`
    
4. Include a copy of chromedriver.exe in each of the Dist folder
```
\dist
    nomad_dist.exe
    chromedriver.exe
```

# -*- mode: python -*-

block_cipher = None


a = Analysis(['nomad_local.py'],
             pathex=['C:\\Users\\estasney\\PycharmProjects\\Nomad_Distributed\\app_folder\\local'],
             binaries=[
                 ('C:\\Users\\estasney\\PycharmProjects\\Nomad_Distributed\\app_folder\\local\\chromedriver.exe',
                  '.')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Nomad_Local',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon='C:\\Users\\estasney\\PycharmProjects\\Nomad_Distributed\\app.ico')

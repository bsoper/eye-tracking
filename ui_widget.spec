# -*- mode: python -*-

block_cipher = None


a = Analysis(['ui_widget.py'],
             pathex=['.', '/Users/bsoper/Dropbox/SeniorYear/Spring/eye_tracking'],
             binaries=[],
             datas=[('/Users/bsoper/Dropbox/SeniorYear/Spring/eye_tracking/haarcascade_*.xml', '.')],
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
          exclude_binaries=True,
          name='ui_widget',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ui_widget')
app = BUNDLE(coll,
             name='ui_widget.app',
             icon=None,
             bundle_identifier=None)

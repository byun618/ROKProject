# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(5000)

block_cipher = None


a = Analysis(['scout_power.py'],
             pathex=['C:\\Users\\sbyun\\Desktop\\rok_member_scanner'],
             binaries=[],
             datas=[('./bin', './bin'),
                    ('./data', './data'),
                    ('./data/original', './data/original'),
                    ('./data/croped', './data/croped'),
                    ('./data/croped/name', './data/croped/name'),
                    ('./data/croped/kill', './data/croped/kill'),
                    ('./data/croped/ds', './data/croped/ds')],
             hiddenimports=[],
             hookspath=['./hooks/'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='scout_power',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

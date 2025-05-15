# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from PyInstaller.utils.hooks import collect_all

def collect_dlls(package_name):
    return collect_all(package_name)[1]

block_cipher = None

a = Analysis(
    ['client_app.py'],
    pathex=[],
    binaries=collect_dlls('pywin32') + [
        (r'venv\Lib\site-packages\bcrypt\_bcrypt.pyd', 'bcrypt')
    ],
    datas=[('local.json', '.'),
        ('img/clear.png', 'img'),
        ('img/icon.ico', 'img'),
        ('version_info.txt', '.')
        ],
    hiddenimports=[
        'bcrypt',
        '_bcrypt',
        'win32com',
        'win32com.client',
        'win32api',
        'win32timezone',
        'pythoncom',
        'pywintypes',
        'sip',
        'PyQt5.sip'
    ] + collect_submodules('win32com'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='img/icon.ico',
)
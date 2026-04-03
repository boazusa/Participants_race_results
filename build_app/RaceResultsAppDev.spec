# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\USER\\Documents\\Python\\running_records\\running_records_windsurf\\flask_app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\USER\\Documents\\Python\\running_records\\running_records_windsurf\\templates', 'templates'), ('C:\\Users\\USER\\Documents\\Python\\running_records\\running_records_windsurf\\static', 'static')],
    hiddenimports=['pandas', 'openpyxl', 'best_results_3plus_or_realtiming_race', 'pytz'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'IPython', 'jupyter', 'notebook', 'pytest', 'sphinx', 'docutils', 'pygments', 'scipy', 'sklearn', 'seaborn', 'nose'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RaceResultsAppDev',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

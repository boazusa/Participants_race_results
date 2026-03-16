# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['flask_app.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static')],
    hiddenimports=['pandas', 'openpyxl', 'best_results_3plus_or_realtiming_race'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'IPython', 'jupyter', 'notebook', 'pytest', 'sphinx', 'docutils', 'pygments', 'setuptools', 'wheel', 'pip', 'conda', 'anaconda', 'scipy', 'sklearn', 'seaborn'],
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
    name='RaceResultsApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

block_cipher = None

a = Analysis(
    ['src/pdf_names_indexer.py'],
     pathex=[],
     binaries=None,
     datas=None,
     hiddenimports=[],
     hookspath=None,
     runtime_hooks=None,
     excludes=['_bootlocale', ],
     cipher=block_cipher
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pdf-names-indexer',
    debug=False,
    upx=False,
)

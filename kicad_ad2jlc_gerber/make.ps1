pip install pyinstaller

# 清理之前的编译
Remove-Item dist, build, jlc_gerber -Recurse -ErrorAction Ignore

# 执行编译
pyinstaller --onefile --name "kicad_ad2jlc_gerber" --add-data "data/gerber.csv;data" --add-data "data/jlc_gerber_header.md;data" --add-data "data/jlc_gerber_header2.md;data" --hidden-import=shutil --hidden-import=csv kicad_ad2jlc_gerber.py

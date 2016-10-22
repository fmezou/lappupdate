pushd ..
node %APPDATA%\npm\node_modules\tiddlywiki\tiddlywiki.js docs\wiki --build
python .\tools\html2text.py .\_build\README.html>.\README.md
python .\tools\html2text.py .\_build\HOWTO.html>.\HOWTO.md
popd
pause
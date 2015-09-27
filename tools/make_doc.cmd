pushd ..
node %APPDATA%\npm\node_modules\tiddlywiki\tiddlywiki.js .\wiki --build lappupdate
node %APPDATA%\npm\node_modules\tiddlywiki\tiddlywiki.js .\wiki --build readme
node %APPDATA%\npm\node_modules\tiddlywiki\tiddlywiki.js .\wiki --build howto
python .\tools\html2text.py .\README.html>.\README.md
python .\tools\html2text.py .\HOWTO.html>.\HOWTO.md
del .\README.html
del .\HOWTO.html
popd
pause
TODO:
- media tag muss arten von medien unterscheiden :/

- Minimizer muss nach Änderungen ausfindig machen, von welchen Templates die Ressource eingebunden wird, und diese dem Changehandler übermitteln: in CH._update_file() eine Funktion aufrufen, die nur die Liste derer Templates findet, die sie selbst einbinden. Diese ruft dann mit parameter "individual" (o.Ä.) notify_changed_template auf und übergibt die Liste. Fertig!

- modular pages
- contact forms
- ftp upload
- blueprints erstellen per command von lokalem verzeichnis, oder URL

- im Bearbeitungsmodus installiertes Paket erstellen, Tests überall ausführbar machen
- "httpwatcher" package nutzen für live server und file watching

# KQL / Eventhouse

Ten scenariusz nie używa Eventhouse ani zapytań KQL jako głównej warstwy. Decyzja jest celowa: problem jest planistyczno-handlowy, a dane 15-minutowe są przetwarzane wsadowo w Lakehouse, notebookach i Warehouse.

Jeżeli w prawdziwym wdrożeniu pozycja miałaby być monitorowana w czasie zbliżonym do rzeczywistego, można dodać Eventstream/Eventhouse dla bieżących odczytów AMI i rynku intraday. W tym repo nie tworzymy pustych artefaktów KQL tylko po to, żeby „użyć” kolejnej funkcji Fabric.

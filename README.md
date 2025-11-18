# kalbeck-tagebuch-data
Data repository for FWF-Projekt [Max Kalbeck: Networking Practices in Vienna 1900](https://www.fwf.ac.at/forschungsradar/10.55776/PAT1123425)


## how to add data

1. (one time only): clone the repo
1. copy [entry-1111-11-11.xml](entry-1111-11-11.xml) into `data/editions/entry-1111-11-11.xml`
1. rename `data/editions/entry-1111-11-11.xml` into `data/editions/entry-{actual-day}.xml`, e.g. [data/editions/entry-1897-01-04.xml](data/editions/entry-1897-01-04.xml)
1. open the copied file `data/editions/entry-{actual-day}.xm` and 
    1. change `<title type="iso-date" when-iso="JJJJ-MM-TT" n="01"/>` into e.g. `<title type="iso-date" when-iso="1897-01-04" n="01"/>`
    1. change `<title level="a">Wochentag, Tag. Monat Jahr</title>` into e.g. `<title level="a">Montag, 4. Jänner 1897</title>`
    1. add current date to `<change who="#hrost" when="JJJ-MM-TT">Dokument angelegt</change>` (or and/or antoher `tei:change` Element)
    1. copy content from [source](https://docs.google.com/document/d/1Z7HdnyobE-B76n8ZL5PBYZzEk3BR_5Da3X5xmpQqum0/edit?tab=t.0) into `<div hand="#hand__kalbeck">` (maybe adapt the `@hand` if necessary), e.g. 
    ```xml
    <div hand="#hand__kalbeck">
        <head/>
        <p/>
    </div>
    ```
    should become something like:
    ```xml
    <div hand="#hand__kalbeck">
        <head>4 Januar Montag.</head>
        <p>
            Mein 47. Geburtstag. Unter d. schriftl. Gratulanten taucht der fatale 
            Milvius wieder auf. Muxl hat eine dramat. Scene gedichtet, die aber 
            so spät fertig geworden ist, daß sie von Paul u. ihr nicht mehr gelernt werden 
            konnte. Paul macht mich zum glückl. Besitzer von Australien: Geographie 
            u. Geschichte interessiren ihn gegenwärtig am meisten. Er zeichnet Asien u. 
            Afrika a. d. Kopfe mit sämmtl. Flüssen, Seen u. Gebirgen, u. schwärmt für 
            Pallas Athene, die ihm noch besser gefällt als Rosl Kantor. Wir 
            eilen ins Cottage zu Baudirektor Müller, der uns v. d. Kauf abrät u. 
            einen eigenen Bau empfiehlt. Bauwissenschaftl. Excursion. Mein Zimmer 
            mit den umherlauernden Clavierbestien u. seiner sonstigen Ruhelosigkeit 
            ist mir schon so sehr verleidet, daß mir jedes Project, das mich von 
            seiner Qual erlöst, [Ausstreichung] ohne weiteres einleuchtet. Ich bin 
            nur neugierig, ob diesmal etwas daraus wird. Nach Tische besuchen 
            mich Frau Flegmann, Ignaz u. Marie Brüll, Frau Kantor, Rosl, Frl. 
            v. Tillemann u. Rittmeister v. Merhal, Karpath, Schneegans – der 
            unglückliche Literatus in spe, Hr. Kohn, gerät dazwischen. Mir ist zu 
            Mute, als ob mein Begräbnis wäre u. die Trauergäste nach der schönen 
            Leiche zusammenkämen. Meine nervöse Unruhe, wenn jemand bei mir ist. 
            Briefe aus Breslau u. Berlin. Den Abend feiere ich mit Schwänzung 
            eines Concerts u. esse – Gottlob! – mit den Kindern mein Hühnchen in Ruhe.
            
        </p>
    </div>
    ```
    1. add linebreaks: `Mein 47. Geburtstag. Unter d. schriftl. Gratulanten taucht der fatale<lb />` use `<lb break="no">` for e.g. `Haus-<lb break="no">tür`
1. check if all document is valid and save
1. check if all documents in `data/editions` are valid (using Oxygen Validation Scenario)
1. commit and push


[source](https://docs.google.com/document/d/1Z7HdnyobE-B76n8ZL5PBYZzEk3BR_5Da3X5xmpQqum0/edit?tab=t.0)


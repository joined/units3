units3
======
This project aims to create an API for the University of Trieste ESSE3 system.

ESSE3 is the web application in which the students data, exams & the like are stored.

ESSE3 doesn't offer any sort of API by itself and this is obviously
restricting if someone wants to 'play' with his university career data.

Why would you want to do that? Let's just say that ESSE3 website doesn't look THAT good, and having the session expire every 15 minutes is really annoying.

## Installation
This project is written in Python 3.4 and it's not backwards-compatibly with Python 2.

Assuming you have are on Linux / OS X and you have already installed `pip` and `virtualenv` (you do, right?),
it's simple as:

    $ git clone https://github.com/joined/units3.git
    $ cd units3
    $ ./setup.sh # creates virtualenv in .env and installs requirements
    New python executable in .env/bin/python
	Installing setuptools, pip...done.
	...
	Cleaning up...
    $ ./run.py   # -h for the help
     * Running on http://127.0.0.1:5000/

On Linux, there seems to be some issues with lxml compilation.
On Debian/Ubuntu you can try to solve them with:

    apt-get install libxslt1-dev libxslt1.1 libxml2-dev libxml2 libssl-dev python-libxml2

For who's thinking _But I use Windows!_: I'm sorry. (I recommend Vagrant!)

## Usage
This API uses HTTP Basic Auth for authentication. When making a request, just use
the same credentials you would have used to log into ESSE3 service.

There are 2 basic types of request that you can do.

1. `/protected/resource_name`
2. `/protected/?select=resource_name_1,resource_name_2,...`

The first is used to retrieve a single resource, the second to retrieve multiple resources at once.

The resources actually implemented are:

+ `home`
+ `pagamenti`
+ `libretto`
+ `prenotazione_appelli`
+ `prenotazioni_effettuate`

They roughly correspond to their respective pages on the ESSE3 service.

I recommend using the excellent [httpie](https://github.com/jakubroztocil/httpie) to test the API (it's like cURL with superpowers). 

Sample request for the `home` resource:

	$ http -a username:password http://localhost:5000/protected/home
	HTTP/1.0 200 OK
	Content-Length: 410
	Content-Type: application/json
	Server: Werkzeug/0.9.6 Python/3.4.1
	{
    	"home": {
        	"anno_di_corso": 1,
        	"corso_di_studio": "[IN00] - INGEGNERIA DELLE BANANE",
        	"data_immatricolazione": "01/01/2023",
        	"matricola": "IN01234567",
        	"nome": "Mario Rossi",
        	"ordinamento": "[IN00-10] - INGEGNERIA DELLE BANANE",
        	"percorso_di_studio": "[PDS0-2010] - comune",
        	"profilo_studente": "Studente Standard",
        	"tipo_di_corso": "Corso di Laurea"
    	}
	}

I plan to add more detailed documentation soon. In the meantime, you can discover
by yourself how the API works by reading the code and making test requests.

## Disclaimer
This project IS NOT connected or affiliated in any way with the University of Trieste.

## License
"THE BEER-WARE LICENSE" (Revision 4.8.12)

<joined@me.com> wrote every file in this repository.
You can do whatever you want with this stuff.
If we meet some day, and you think this stuff is worth it, you can buy me a beer
in return.

Lorenzo Gasparini
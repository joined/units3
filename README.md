units3
======
This project aims to create an API for the University of Trieste ESSE3 system.

ESSE3 is the web application in which the students data, exams & the like are stored.

ESSE3 doesn't offer any sort of API by itself and this is obviously
restricting if someone wants to 'play' with his university career data.

Why would you want to do that? Let's just say that ESSE3 website doesn't look that good, and having the session expire every 15 minutes is really annoying.

## Installation
To ease development to everyone, I set up a Vagrantfile and a provisioning script
to get up & running without any hassle (if you don't know what Vagrant is, check out [this link](http://vagrantup.com))

    joined@mb:~$ git clone https://github.com/joined/units3.git
    joined@mb:~$ cd units3/vagrant
    joined@mb:~/units3/vagrant$ vagrant up
    Bringing machine 'default' up with 'virtualbox' provider...
    ...
    Cleaning up...
    joined@mb$ vagrant ssh
    vagrant@vagrant-ubuntu-trusty-64:~$ cd units3
    vagrant@vagrant-ubuntu-trusty-64:~/units3$ ./run.py -v # -h for help
       * Running on http://0.0.0.0:5000/

###Vagrant configuration

+ Latest Ubuntu 14.04 LTS system
+ 1024 mb of RAM (512 mb is not enough to compile lxml)
+ 2 cpus shared
+ Guest port 5000 forwarded to host port 8080.
+ Root of repository synced with `/home/vagrant/units3/`

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

```
joined@mb$ http -a username:password http://localhost:8080/protected/home
HTTP/1.0 200 OK
Content-Length: 410
Content-Type: application/json
Server: Werkzeug/0.9.6 Python/3.4.1
```

```json
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
```

I plan to add more detailed documentation soon. In the meantime, you can discover
by yourself how the API works by reading the code and making test requests.

## Todo

+ Move to Docker as provider for Vagrant, to improve performance and provide near-zero overhead when running on Linux. Vagrant is able to understand where it is running and provide a lightweight VM (boot2docker) if the host OS is not Linux. This way everyone's happy :)

## Disclaimer
This project IS NOT connected or affiliated in any way with the University of Trieste.

## License
"THE BEER-WARE LICENSE" (Revision 4.8.12)

<joined@me.com> wrote every file in this repository.
You can do whatever you want with this stuff.
If we meet some day, and you think this stuff is worth it, you can buy me a beer
in return.

Lorenzo Gasparini
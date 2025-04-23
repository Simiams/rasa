## CHATBOT

Pour lancer la base de donnée executez la commande suivante :

```bash
docker-compose up -d
```

Lancer les action

```bash
rasa run actions
```

Lancer le serveur Rasa

```bash
rasa run -m models --enable-api --cors "*" -p 5005
```

Lancer le bot discord

```bash
python3 discord_channel.py 
```
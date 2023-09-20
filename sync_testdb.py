import subprocess

# Configuration des serveurs et bases de données
serveur_source = {
    'host': 'localhost',
    'user': 'syncro',
    'database_prod': 'AeroP_ProdDB'
}

serveur_esclave = {
    'host': '192.168.113.208',
    'user': 'syncro',
    'database_test': 'AeroP_TestDB'
}

# Fonction pour synchroniser la base de données de test avec la base de données de prod
def synchroniser_base_de_donnees():
    print("Synchronisation des bases de données en cours...")

    # Vérifier si la base de données 'AeroP_TestDB' existe sur le serveur Test
    cmd = ['psql', '-h', serveur_esclave['host'], '-U', serveur_esclave['user'], '-d', 'postgres', '-t', '-c', 'SELECT datname FROM pg_database;']
    dbs = subprocess.check_output(cmd, universal_newlines=True).split()

    if serveur_esclave['database_test'] in dbs:
    	# Supprimer la base de données existante 'AeroP_TestDB' sur le serveur Test
    	subprocess.run(['dropdb', '-h', serveur_esclave['host'], '-U', serveur_esclave['user'], serveur_esclave['database_test']])
    	print("Base de données 'AeroP_TestDB' supprimée sur le serveur Test.")

    # Créer une sauvegarde personnalisée de la base de données de prod
    subprocess.run(['pg_dump', '-h', serveur_source['host'], '-U', serveur_source['user'], '-d', serveur_source['database_prod'], '-F', 'c', '-f', 'backup.dump'])
    print("Sauvegarde de la base de données de prod du serveur Prod effectuée.")

    # Créer la base de données 'syncdb' sur le serveur Test avec le propriétaire 'testuser'
    subprocess.run(['createdb', '-h', serveur_esclave['host'], '-U', serveur_esclave['user'], '-O', 'testuser', serveur_esclave['database_test']])
    print("Base de données 'syncdb' créée sur le serveur Test avec le propriétaire 'testuser'.")

    # Restaurer la base de données 'syncdb' sur le serveur Test à partir de la sauvegarde
    subprocess.run(['pg_restore', '-h', serveur_esclave['host'], '-U', serveur_esclave['user'], '-d', serveur_esclave['database_test'], 'backup.dump'])
    print("Base de données 'syncdb' du serveur Test mise à jour avec la sauvegarde de la prod du serveur Prod.")

    # Nettoyer le fichier de sauvegarde local
    subprocess.run(['rm', 'backup.dump'])
    print("Nettoyage des fichiers temporaires...")

    print("Synchronisation terminée.")

# Fonction pour recréer la branche test basée sur la branche de prod du serveur 1
def recreer_branche_test():
    print("Recréation de la branche 'test' en cours...")

    subprocess.run(['git', 'branch', '-D', 'test'])  # Supprimer la branche test

    # Créer une nouvelle branche test basée sur la branche de prod du serveur 1
    subprocess.run(['git', 'checkout', '-b', 'test', 'prod'])

    # Pousser la nouvelle branche vers le dépôt distant
    subprocess.run(['git', 'push', 'origin', 'test'])
    print("Branche 'test' recréée et poussée vers le dépôt distant.")

# Fonction principale
def main():
    # Exécute la synchronisation des bases de données
    synchroniser_base_de_donnees()

    # Recrée la branche de test basée sur la branche de prod du serveur 1 et pousse les changements
    #recreer_branche_test()

# Appeler la fonction principale
if __name__ == "__main__":
    main()

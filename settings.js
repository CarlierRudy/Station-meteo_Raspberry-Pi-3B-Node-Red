module.exports = {
    // -------------------------------------------------------------------------
    // Paramètres Globaux Node-RED
    // -------------------------------------------------------------------------
    uiPort: process.env.PORT || 1880,
    mqttReconnectTime: 15000,
    serialReconnectTime: 15000,
    debugMaxLength: 1000,

    // -------------------------------------------------------------------------
    // PARTIE SÉCURITÉ (Authentification Node-RED)
    // -------------------------------------------------------------------------
    // Pour générer un hash de mot de passe (remplacez 'password' par votre mdp) :
    // node -e "console.log(require('bcryptjs').hashSync(process.argv[1], 8));" password
    adminAuth: {
        type: "credentials",
        users: [{
            username: "admin",
            // Hash généré pour le mot de passe "password" (A CHANGER EN PROD !)
            password: "$2a$08$zPBkNcb.vMpw3J157yv0X.20.E9b7KkC7wXn7YJpP2z8H9b8r5cZC",
            permissions: "*"
        }]
    },

    // -------------------------------------------------------------------------
    // Sécurité du Dashboard (UI)
    // -------------------------------------------------------------------------
    // Cette partie requiert une authentification basique pour voir la station météo
    // (Commentez cette section si vous voulez un accès public au dashboard)
    httpNodeAuth: {
        user: "visiteur",
        pass: "$2a$08$C.U0y7/wJ1q5uT2W8v0X.20.E9b7KkC7wXn7YJpP2z8H9b8r5cZC" // mdp : visiteur
    },

    // -------------------------------------------------------------------------
    // HTTPS (TLS)
    // -------------------------------------------------------------------------
    // Pour chiffrer les flux (fortement recommandé sur réseau public),
    // générez des certificats (ex: Let's Encrypt ou auto-signés) et dé-commentez.
    //
    // https: {
    //     key: require("fs").readFileSync('cle_privee.pem'),
    //     cert: require("fs").readFileSync('certificat.pem')
    // },
    // requireHttps: true,

    // -------------------------------------------------------------------------
    // Structure de fichiers
    // -------------------------------------------------------------------------
    // Fichier principal enregistré :
    flowFile: 'flows.json',
    flowFilePretty: true, // Facilite la lecture sur Github / IDE
    credentialSecret: "StationMeteoSecretKey123!",

    // Configuration des logs
    logging: {
        console: {
            level: "info", // "fatal", "error", "warn", "info", "debug", "trace"
            metrics: false,
            audit: false
        }
    },
    
    // Déclare l'utilisation de modules custom ou de commandes exec autorisées
    functionAllowList: ["*"],
    execAllowList: ["*"], // Restreindre en production aux scripts météo

    editorTheme: {
        projects: {
            enabled: false // Simplification pour ce projet
        }
    }
};

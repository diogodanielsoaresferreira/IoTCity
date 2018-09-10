// Initialize Firebase
var config = {
    apiKey: "AIzaSyBmHtlfbS5qjpvRQjv3LkRKqO6wnEqCxTI",
    authDomain: "iotcity-97beb.firebaseapp.com",
    databaseURL: "https://iotcity-97beb.firebaseio.com",
    projectId: "iotcity-97beb",
    storageBucket: "iotcity-97beb.appspot.com",
    messagingSenderId: "255744133302"
};
firebase.initializeApp(config);

// Retrieve Firebase Messaging object.
const messaging = firebase.messaging();

navigator.serviceWorker.register('/static/admin-lte/dist/js/firebase-messaging-sw.js')
.then((registration) => {
  messaging.useServiceWorker(registration);
   messaging.onTokenRefresh(function() {
      messaging.getToken()
      .then(function(refreshedToken) {
        //console.log('Token refreshed.');
        // Indicate that the new Instance ID token has not yet been sent to the
        // app server.
        setTokenSentToServer(false);
        // Send Instance ID token to app server.
        sendTokenToServer(refreshedToken);
        // [START_EXCLUDE]
        // Display new Instance ID token and clear UI of all previous messages.
        resetUI();
        // [END_EXCLUDE]
      })
      .catch(function(err) {
        console.log('Unable to retrieve refreshed token ', err);
        //showToken('Unable to retrieve refreshed token ', err);
      });

  });
});

messaging.onMessage(function(payload) {
        console.log("Message received. ", payload);
        // [START_EXCLUDE]
        // Update the UI to include the received message.
        //appendMessage(payload);
        const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: '/static/admin-lte/dist/img/iotcity.png',
            };
             if (!("Notification" in window)) {
                console.log("This browser does not support system notifications");
            }
            // Let's check whether notification permissions have already been granted
            else if (Notification.permission === "granted") {

            // If it's okay let's create a notification
                var notification = new Notification(notificationTitle,notificationOptions);

                notification.onclick = function(event) {
                    event.preventDefault(); // prevent the browser from focusing the Notification's tab
                    window.open( "/alerts" , '_blank');
                    notification.close();
                }
            }
        // [END_EXCLUDE]
      });

function resetUI() {
    // [START get_token]
    // Get Instance ID token. Initially this makes a network call, once retrieved
    // subsequent calls to getToken will return from cache.

    console.log("getting token")
    messaging.getToken().then((resp) => {
      console.log(resp)
    })
    messaging.getToken()
    .then(function(currentToken) {
      console.log("Got current token")
      if (currentToken) {
        sendTokenToServer(currentToken);
      } else {
        // Show permission request.
        console.log('No Instance ID token available. Request permission to generate one.');
        // Show permission UI.
        setTokenSentToServer(false);
      	requestPermission();
      }
    })
    .catch(function(err) {
      console.log('An error occurred while retrieving token. ', err);
      //showToken('Error retrieving Instance ID token. ', err);
      setTokenSentToServer(false);
    });
    console.log("End get token")

  }
function requestPermission() {
    console.log('Requesting permission...');
    // [START request_permission]
    messaging.requestPermission()
    .then(function() {
      console.log('Notification permission granted.');

      // TODO(developer): Retrieve an Instance ID token for use with FCM.
      // [START_EXCLUDE]
      // In many cases once an app has been granted notification permission, it
      // should update its UI reflecting this.
      resetUI();
      // [END_EXCLUDE]
    })
    .catch(function(err) {
      //console.log('Unable to get permission to notify.', err);
    });
    // [END request_permission]
  }

function showToken(currentToken) {
    // Show token in console and UI.
    //console.log(currentToken)
}

function sendTokenToServer(currentToken) {
    if (!isTokenSentToServer()) {
      try{
        console.log('Sending token to server...');
        fetch('http://178.62.255.129/devices/', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
          'registration_id': currentToken,
          'type': 'web',
        }),
        credentials: "include",
      }).then(function(response) {
        console.log(response);
      })
      setTokenSentToServer(true);
    }
    catch(err){
      setTokenSentToServer(false);
      console.log('Could not send token to server');
    }
      
    } else {
      console.log('Token already sent to server so won\'t send it again ' +
          'unless it changes');
    }

  }

function isTokenSentToServer() {
  return false;
    if (window.localStorage.getItem('sentToServer') == 1) {
          return true;
    }
    return false;
  }

function setTokenSentToServer(sent) {
    if (sent) {
      window.localStorage.setItem('sentToServer', 1);
    } else {
      window.localStorage.setItem('sentToServer', 0);
    }
  }

// Add a message to the messages element.
  function appendMessage(payload) {
  }

  resetUI();
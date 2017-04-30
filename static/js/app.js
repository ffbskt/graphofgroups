'use strict';
//Page and controllers
var app = angular.module('conferenceApp',
    ['conferenceControllers', 'ngRoute', 'ui.bootstrap']).
    config(['$routeProvider',
        function ($routeProvider) {
            $routeProvider.
                when('/', {
                    templateUrl: '/partials/main.html',
		    //templateUrl: '/partials/home.html'
                    controller: 'RootCtrl' 
                }).
		when('/group/:websafeConferenceKey', {
                    templateUrl: '/partials/group.html',
                    controller: 'EditGroupCtrl'
                }).
		when('/user/:websafeConferenceKey', {
                    templateUrl: '/partials/user.html',
                    controller: 'R2Ctrl'
                }).
		when('/create_group', {
                    templateUrl: '/partials/create_group.html',
                    controller: 'CreateGroupCtrl'
                }).
		when('/allgroups', {
                    templateUrl: '/partials/allgroups.html',
                    controller: 'AllGroupCtrl'
                }).
                otherwise({
                    redirectTo: '/'
                });
        }]);

app.constant('HTTP_ERRORS', {
    'UNAUTHORIZED': 401
});


// Google autenticasion
app.factory('oauth2Provider', function ($modal) {
    var oauth2Provider = {
        CLIENT_ID: 'your client key same as in GG.py',
        SCOPES: 'email profile',
        signedIn: false
    }

    /**
     * Calls the OAuth2 authentication method.
     */
    oauth2Provider.signIn = function (callback) {
        gapi.auth.signIn({
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'accesstype': 'online',
            'approveprompt': 'auto',
            'scope': oauth2Provider.SCOPES,
            'callback': callback
        });
    };

 oauth2Provider.signOut = function () {
        gapi.auth.signOut();
        // Explicitly set the invalid access token in order to make the API calls fail.
        gapi.auth.setToken({access_token: ''})
        oauth2Provider.signedIn = false;
    };

    /**
     * Shows the modal with Google+ sign in button.
     *
     * @returns {*|Window}
     */
    oauth2Provider.showLoginModal = function() {
        var modalInstance = $modal.open({
            templateUrl: '/partials/login.modal.html',
            controller: 'OAuth2LoginModalCtrl'
        });
        return modalInstance;
    };

    oauth2Provider.show = function(pic) {
	oauth2Provider.pic = 'data:image/jpeg;base64,' +pic;
   	//gapi.client.rrrq.show_picture({'mail':mail, 'pname':pic}).execute(function (resp) {
		//alert(99)
		//oauth2Provider.img = resp.picture;
		//alert($scope.img);
	    //});	
	console.log(1, pic)
        var modalInstance = $modal.open({
            templateUrl: '/partials/picture.model.html',
            controller: 'PictCtrl'//'OAuth2LoginModalCtrl'
        });
        return modalInstance;
    }

    return oauth2Provider;
});

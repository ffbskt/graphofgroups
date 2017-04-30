'use strict';
var conferenceApp = conferenceApp || {};
conferenceApp.controllers = angular.module('conferenceControllers',['ui.bootstrap']);

var TMAIL = '';
var LISENS_AGREEMENT = "При нажатии 'ok' вы разрешаете нам использовать свою личную информацию (выложенную вами на данном сайте и дополненную нашей информацией о вас) сделав ее общедоступной, кто угодно после некоторых процедур имеет право посмотреть, передать (в том числе и за границу РФ) и дополнить данную информацию.  Так же ваша информация может быть использована нами в комерческих целях. Так же более подробная информация \nhttps://docs.google.com/document/d/1imo04Jy69C7giWQsdZ8U9m0S2d25ZfvKpNSnQ0LIzT4/pub"

conferenceApp.controllers.controller('RootCtrl', function ($scope, $location, oauth2Provider) {

    $scope.whom_show = ''; // Кому показывают данные
    $scope.tmail_this = ''; // Кого показывают
    $scope.response = {};
    $scope.uname = '' || $scope.uname;	
    $scope.history = {}		
    $scope.history.time_in = new Date()
    $scope.history.url = $location.path()		
    //$scope.own_page = $location.search()
    $scope.isActive = function (viewLocation) {
	//console.log($scope.own_page, viewLocation, $location.path())
        return viewLocation === $location.path();
    };	    
	
    $scope.getSignedInState = function () {
        return oauth2Provider.signedIn;
    };

    $scope.registration = function () {
        gapi.client.rrrq.add_user({'mail':$scope.tmail_this, 'name':$scope.uname}).execute(function (resp) {
	console.log('r', resp.ans, $scope.uname);
	});
	$scope.history.val = [$scope.uname]
	$scope.history.action = ["@registration"]
	gapi.client.rrrq.timer($scope.history).execute(function (resp) {console.log('dest2', $scope.history)});
    };

    $scope.signIn = function () {
        oauth2Provider.signIn(function () {
            gapi.client.oauth2.userinfo.get().execute(function (resp) {
                $scope.$apply(function () {
                    if (resp.email) {
                        oauth2Provider.signedIn = true;
                        $scope.alertStatus = 'success';
			$scope.tmail_this = resp.email;
			$scope.uname = resp.name;
			console.log('r', resp.name);
			$scope.registration();	
			}

			//$scope.rootMessages = $scope.mail;
                    
                });
            });
        });		
    };


//-----------------------------------------------
    $scope.initSignInButton = function () {
        gapi.signin.render('signInButton', {
            'callback': function () {
                jQuery('#signInButton button').attr('disabled', 'true').css('cursor', 'default');
                if (gapi.auth.getToken() && gapi.auth.getToken().access_token) {
                    $scope.$apply(function () {
                        oauth2Provider.signedIn = true;
                    });
                }
            },
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'scope': oauth2Provider.SCOPES
        });
    };

    /**
     * Logs out the user.
     */
    $scope.signOut = function () {
        oauth2Provider.signOut();
        $scope.alertStatus = 'success';
        $scope.rootMessages = 'Logged out';
    };

    /**
     * Collapses the navbar on mobile devices.
     */
    $scope.collapseNavbar = function () {
        angular.element(document.querySelector('.navbar-collapse')).removeClass('in');
    };
    
    
});

//________________________Home Page_______________________________________________

conferenceApp.controllers.controller('R2Ctrl', function ($scope, $location, oauth2Provider, $routeParams) { 
    
    //function MyCtrl($scope) {
    $scope.url = null	
    $scope.data = 'none';
    $scope.groups = []
    $scope.top = {}		
    $scope.history = {}		
    $scope.history.time_in = new Date()
    $scope.history.url = $location.path()
    $scope.history.action = []
    $scope.history.obj = []
    $scope.history.val = []
    var history_backet = {}
	history_backet.st = []
	history_backet.gr = []					
    $scope.add = function(g_ind, st_ind){
      var f = document.getElementById('file').files[0],
          r = new FileReader();
      r.onloadend = function(e){
        $scope.q.stat_block[g_ind].st_def[st_ind] = f['name'] + ';' + e.target.result;
	//console.log('r', e.target.result[10].toString())
      }
      //r.readAsBinaryString(f);
	//r.readAsArrayBuffer(f)
	r.readAsDataURL(f)
  	console.log('q', g_ind, st_ind, r,' !', f['name'])	
	//$scope.q.st_def[ind] = f//document.getElementById('file').files[0]
	//console.log('q', $scope.q.st_def[ind])
    };
//}

    	
    $scope.submitted = false;
    $scope.loading = false;
    $scope.$watch($scope.getSignedInState, function () {
	//$scope.timer.on = new Date()
    	if (oauth2Provider.signedIn) {
		$scope.showUser();
    	}
    })
    $scope.q = 0	
    $scope.showUser = function () {
	//console.log($scope.tmail_this)
	var retrieveProfileCallback = function () {
		console.log('rq', $location.path().substring(0,5))
	    if ('/user' == $location.path().substring(0,5)) {
		console.log('rq2', $routeParams.websafeConferenceKeye)
		$scope.url = $routeParams.websafeConferenceKey
	    };	
            $scope.loading = true;
            gapi.client.rrrq.show_user({'whom_show':$scope.whom_show, 'tmail_this':$scope.tmail_this, 'url':$scope.url}).execute(function (resp) {
			//alert('p',$scope.mail)
                        $scope.$apply(function () {
                        $scope.loading = false;
			$scope.q = resp;
			console.log('q12', $scope.q);
			for (var i = 0; i < $scope.q.stat_block.length; ++i) {
			    $scope.q.stat_block[i].return_ch = [];
			    $scope.groups.push($scope.q.stat_block[i].group_url)	
			    console.log('q3', $scope.groups, $scope.q.stat_block[i]);
			    $scope.groups[0] = 'ahFkZXZ-dW5pdmVyc2l0eWdpbXI3CxIFR3JvdXAiEGZmYnNrdEBnbWFpbC5jb20MCxIFR3JvdXAiEUdlbmVyYWwgcGFyYW1ldHJzDA'		 	///GUT!!!!!!!!!
			}
			console.log('q4', $scope.groups);
			//$scope.showTop()
                      });
               });
           };

	   // Запуск в случае аутифекации, если нет сообщение регистрации
	   if (!oauth2Provider.signedIn) {
		$scope.singIn;
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then(retrieveProfileCallback);
            } else {		
                retrieveProfileCallback();
            }
        };
    
    $scope.showTop = function () { 
	gapi.client.rrrq.output_rate({'urls':$scope.groups}).execute(function (resp) {
		$scope.$apply(function () {
		    $scope.top = resp
		    console.log('TOP',$scope.top, $scope.groups) 	
		});
	});
    };		

    $scope.saved_alert = function(){alert('saved');
    }; 
    $scope.$on("$destroy", function(){
	$scope.history.time_out = new Date()
	//alert('destroy')
	//console.log('on ', $scope.history.timer_on, 'off', $scope.history.timer_off, 'interval', $scope.history.time_on - $scope.history.timer_off, $location.path())
	$scope.editUser();
	gapi.client.rrrq.timer($scope.history).execute(function (resp) {console.log('dest2', $scope.history)});
	console.log('dest', $scope.history)
	$scope.history.action = []
        $scope.history.obj = []
	
        $scope.history.val = []
	
	history_backet.gr = []
	history_backet.st = []
	
    });
    
    //var ss = new Set();		
    $scope.line_change = function (g_ind, st_ind) {
	
	if ($scope.q.stat_block[g_ind].return_ch.indexOf(st_ind) == -1) {
	    $scope.q.stat_block[g_ind].return_ch.push(st_ind);
	    console.log('aaaa', g_ind, st_ind, $scope.q.stat_block[g_ind].st_name[st_ind])
	    history_backet.st.push(st_ind);
	    history_backet.gr.push(g_ind);
	}
	console.log('aaaa2', g_ind, st_ind, history_backet.st, history_backet.gr)
	//console.log('aaaa2', g_ind, st_ind, $scope.q.stat_block[1])
    }
     
    //----
    $scope.editUser = function () {
	// Сохраняем что было изменено Добавляем в историю
	
	for (var j=0; j < history_backet.gr.length; ++j) {
		var st_ind = history_backet.st[j]
		var g_ind = history_backet.gr[j]
		console.log('aaaa3', st_ind, g_ind, $scope.q.stat_block[g_ind].st_def[st_ind])
		$scope.history.action.push($scope.q.stat_block[g_ind].st_name[st_ind])
		if ($scope.q.stat_block[g_ind].st_def[st_ind].length > 30) {
		    $scope.history.val.push($scope.q.stat_block[g_ind].st_def[st_ind].substring(0,30));
		} else {
			console.log('q',$scope.history.val)
		    $scope.history.val.push($scope.q.stat_block[g_ind].st_def[st_ind]);
		}	          
		if ('group_url' in $scope.q.stat_block[g_ind]) {
			$scope.history.obj.push($scope.q.stat_block[g_ind].group_url)
		} else {
			$scope.history.obj.push("General parametrs")
		}
		console.log($scope.q.stat_block[g_ind].st_def[st_ind])
		console.log($scope.q.stat_block[g_ind].st_name[st_ind])
	}
	console.log('HIST:', $scope.history.action, $scope.history.val, $scope.history.obj)
	gapi.client.rrrq.edit_user($scope.q). execute(function (resp) {})
	history_backet.gr = []
	history_backet.st = []
	for (var j=0; j < $scope.q.stat_block.length; ++j) {
	    $scope.q.stat_block[j].return_ch = []; 
	}
    };
});




//__________________________________Your Groups___________________________________

conferenceApp.controllers.controller('EditGroupCtrl', function ($scope, $log, oauth2Provider, $routeParams, HTTP_ERRORS, $location) {
	$scope.$watch($scope.getSignedInState, function () {
if (oauth2Provider.signedIn) {$scope.showGroup();}
    })
	var history = history || {} 
    	history.time_in = new Date()
    	
    	history.action = history.action || [] 
    	history.obj = history.obj || []
    	history.val = history.val || []	 
	var history_backet = {}
	history_backet.st = [];
	history_backet.usr = [];
	history_backet.blk = [];
	$scope.us_ind = {};
    	$scope.g=$routeParams.websafeConferenceKey;	
    	history.url = $scope.g
    	$scope.gr = [];
    	$scope.a = {};
    	$scope.selection = [];
	$scope.mess='';
	$scope.nfc=null;
	$scope.user_mail=null;
	$scope.nfc_resp = '';
	$scope.show_role = $scope.show_role || false;
        $scope.editCh = function(sh) {
	    $scope.show_role=!sh};
	$scope.editRole = function(user_url, role, is_add) {
	    gapi.client.rrrq.edit_role({'user_url':user_url, 'group':$scope.g, 'role':role, 'is_add':is_add}).execute(function (resp) {});
	};
	
	$scope.timer = {}        
	$scope.show = function(pic_name, obj_url){
	    console.log('123sh', pic_name, obj_url)
	    gapi.client.rrrq.show_picture({'obj_url':obj_url, 'pname':pic_name}).execute(function (resp) {
	$scope.img = 'data:image/jpeg;base64,' + resp.picture;
	console.log('123sh2', pic_name, obj_url, $scope.img)
	oauth2Provider.show(resp.picture);
	});	
	    //$mdDialog.show({
      //controller: EditGroupCtrl,
      //templateUrl: '/partials/picture.model.html'
	//    });
		
	};
	$scope.addMessage = function() {
     	     gapi.client.rrrq.add_chat({"group_url": $routeParams.websafeConferenceKey, "value":$scope.mess}).execute(function (resp) {
		console.log('e-', $scope.mess, $scope.g);
		
		$scope.showGroup();
	});
	};
	$scope.addNFC = function() {
     	     gapi.client.rrrq.use_card({"group_url": $routeParams.websafeConferenceKey, "card_id":$scope.nfc, "child_object":$scope.user_mail, "stat_pls":'visit'}).execute(function (resp) {
		console.log('e-', $scope.nfc, $scope.g, $scope.user_mail);
		$scope.nfc = null
		$scope.nfc_resp = resp
		$scope.showGroup();
	});
	};
    	// Отмечаем кого пометили на добавление
    	$scope.joinAccept = function(url, role) {
    		$scope.selection.push(url);
		$scope.selection.push(role);
    		console.log($scope.selection);	
    	};	

   	//$scope.$watch($scope.init, function () {
   		//alert($scope.g!='')

		//$timeout(console.log('i', $scope.g), 1000))
		//if ($scope.g != '') {
			//$scope.showGroup();
		//}
	 // })
    	
	$scope.$on("$destroy", function(){
		$scope.saveChange();
		console.log('SChenge');
    	});
//---------------------------------------------------
       	$scope.showGroup = function () {
		//alert($scope.tmail_this)
		var InitCallback = function () {
		$scope.timer.on = new Date()
		gapi.client.rrrq.show_group({
			"group_url": $routeParams.websafeConferenceKey, "tmail_this":TMAIL
            		//direct_url: $routeParams.websafeConferenceKey
        	}).execute(function (resp) {
			//alert(11)
			//$scope.change = resp
        		$scope.$apply(function () {
        			$scope.loading = false;
                		if (resp.error) {
                    			// The request has failed.
                    			var errorMessage = resp.error.message || '';
                    			$scope.messages = 'Failed to get the conference : ' + $routeParams.websafeKey + ' ' + errorMessage;
                   			$scope.alertStatus = 'warning';
                    			$log.error($scope.messages);
                		} 
				else {
                    			// The request has succeeded.
                    			$scope.alertStatus = 'success';
		    			$scope.a = resp;
					//$scope.g = $routeParams.websafeConferenceKey; 
		    			console.log('if change', $scope.a.user_group_stat, $scope.tmail_this );
		
			for (var i = 0; i < $scope.a.user_group_stat.length; ++i) {
			    $scope.a.user_group_stat[i].stat_block[0].return_ch = [];
		 	    if ($scope.a.user_group_stat[i].stat_block.length > 1) {
			        $scope.a.user_group_stat[i].stat_block[1].return_ch = [];
				}
					}
                		}
            		});
        	});
		};
		if (!oauth2Provider.signedIn) {
		//$scope.singIn;
                //var modalInstance = oauth2Provider.showLoginModal();
                //modalInstance.result.then(InitCallback);
            } else {		
                InitCallback();
            }
		
		
	};

 //----prove
    $scope.changed = function (i, ind, ind_2, blk, m, pls) {
	if ($scope.a.user_group_stat[ind].stat_block[blk].return_ch.indexOf(ind_2) == -1) {
	    $scope.a.user_group_stat[ind].stat_block[blk].return_ch.push(ind_2);
	    history_backet.st.push(ind_2);
	    history_backet.usr.push(ind);
	    history_backet.blk.push(blk);
	}
	
	if (pls) {
		i = parseInt(i) + pls;
		console.log('def', i, ind, ind_2);	
	};
	
	$scope.a.user_group_stat[ind].stat_block[blk].st_def[ind_2] = i.toString();
	//$scope.a.user_group_stat[ind].key_value = m;   // delete?
	//console.log('if change h1', i, $scope.a.user_group_stat[ind].if_change, ind, m, ind, ind_2);
	console.log('len1', ind, ind_2, i, $scope.a.user_group_stat[ind].stat_block[blk].group_url);
	$scope.us_ind[ind.toString()] = ind;
	return i;
    };    

    
    
    $scope.saveChange = function () {
	//alert(9)
	//console.log('len2', $scope.us_ind.length, $scope.us_ind[-1])
	var keys = Object.keys($scope.us_ind);
	for (var j = 0; j < keys.length; ++j) {
	    var i = keys[j];
	
	console.log('in', i);
	  gapi.client.rrrq.edit_user($scope.a.user_group_stat[i]).
                    execute(function (resp) {console.log(45, resp)})
	  console.log($scope.a.user_group_stat[i], i, '==', $scope.us_ind[i])
	}
	//Add users
 	
	for (var i = 0; i < $scope.selection.length; i+=2) {
	  //try {
	  console.log('i in scs', i)
	  var g_url = 0
	  gapi.client.rrrq.put_object_to_group({"child_url":$scope.selection[i], 'group_url':$scope.g, 'role':$scope.selection[i+1]}).
                    execute(function (resp) {console.log('m', $scope.a.ask_join)})
	//} catch (e) {console.log('ask join exception')}
	}
	
	$scope.us_ind = {};
	$scope.selection = []
    };	
	
	$scope.$on("$destroy", function(){
	    history.time_out = new Date()
	    for (var j=0; j < history_backet.usr.length; ++j) {
	
		var st = history_backet.st[j]
		var blk = history_backet.blk[j]
	 	var usr = history_backet.usr[j]
		console.log('gra3', st, usr, $scope.a.user_group_stat[usr].stat_block[blk].st_def[st])
		history.action.push($scope.a.user_group_stat[usr].url)
		if ($scope.a.user_group_stat[usr].stat_block[blk].st_def[st].length > 30) {
		    history.val.push($scope.a.user_group_stat[usr].stat_block[blk].st_def[st].substring(0,30));
		} else {
			console.log('group',history.val)
		    history.val.push($scope.a.user_group_stat[usr].stat_block[blk].st_def[st]);
		}	          
		// + blk
		history.obj.push($scope.a.user_group_stat[usr].stat_block[blk].st_name[st])
	    }	
	    gapi.client.rrrq.timer(history).execute(function (resp) {console.log('Gr2', history)});	
	});	
	
  
});

//______________________________All Group_________________________________________

conferenceApp.controllers.controller('AllGroupCtrl',
    function ($scope, $log, oauth2Provider, $routeParams, HTTP_ERRORS, $location) {
	$scope.$watch($scope.getSignedInState, function () {
if (oauth2Provider.signedIn) {$scope.allGroups();}
    })

	var history = history || {} 
    history.time_in = new Date()
    history.url = $location.path()
    history.action = history.action || [] 
    history.obj = history.obj || []
    history.val = history.val || []	
    $scope.add_group={};
    //$scope.add_groupadd_select_group = '';
    $scope.chose_group = false;	
	$scope.allGroups = function () {
	
	    //alert('13', $scope.tmail_this)
	var InitCallback = function () {
	    gapi.client.rrrq.all_group().execute(function (resp) {
	$scope.$apply(function () {
          $scope.loading = false;
	//alert('2', $scope.tmail_this)
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to get the conference : ' + $routeParams.websafeKey
                        + ' ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);
                } else {
                    // The request has succeeded.
                    $scope.alertStatus = 'success';
                    $scope.all_groups = resp
		    //console.log('1',resp.invited_m[0])
                }
            });
				
	});
	};
	if (!oauth2Provider.signedIn) {
		$scope.signIn();
		$scope.getSignedInState();
		//console.log(99)
		InitCallback();
                //var modalInstance = oauth2Provider.showLoginModal();
                //modalInstance.result.then(InitCallback);
            } else {
		try {
			console.log('t');
			InitCallback();
		} 
		catch (e) {
			$scope.signIn();
		$scope.getSignedInState();
		//console.log(90);
                InitCallback();
		}
		
            }   
        };

	/*$scope.groupJoin = function (name) {
	console.log(1, name) 	
	if( name != '' ){
	alert(1, name)
	 gapi.client.rrrq.ask_to_join({'group_url':url, 'child_object':, 'child_gr_author'}).execute(function (resp) {
		alert("Your request will be considered", name);
		history.action.push('user_join')
		history.obj.push(resp.url)
		//console.log('1',resp);
	  });
	} else {};
    };*/
	

    $scope.$on("$destroy", function(){
	    history.time_out = new Date()
	    gapi.client.rrrq.timer(history).execute(function (resp) {console.log('allg2', $scope.history)});	
	});	

			
    $scope.askJoin = function (url, child_object, child_gr_author) {
	var retVal = true;
	var action = 'group_join ' + child_object
	if (child_gr_author == null) {  
	    retVal = confirm(LISENS_AGREEMENT);
	    action = 'user_join'	
	}
	if( retVal == true ){
	alert(1, url, child_object, child_gr_author)
	  gapi.client.rrrq.ask_to_join({'group_url':url, 'child_object':child_object, 'child_gr_author':child_gr_author}).execute(function (resp) {
		alert("Your request will be considered", child_object);
		history.action.push(action)
		history.obj.push(url)
		console.log('1', resp, child_object, child_gr_author);
	  });
	} else {};
    };

    $scope.agreeJoin = function (m, g, r) {
	var retVal = confirm(LISENS_AGREEMENT);
	if( retVal == true ){
	//alert(1, x)
	  gapi.client.rrrq.put_object_to_group({'child_object':m,'group_name':g, 'role':r,}).execute(function (resp) {
		alert("Ok");
		//console.log('1',resp);
	  });
	} else {};
    };

});
//_________________________PictureCntrl______________________________________________________________
conferenceApp.controllers.controller('PictCtrl',
    function ($scope, $log, oauth2Provider, $routeParams, HTTP_ERRORS) {
	//$scope.img = 'data:image/jpeg;base64,' + oauth2Provider.img;
	//$scope.img
	//$scope.img = oauth2Provider.pic
	$scope.showPict = function () {
	    //mail = oauth2Provider.pd[2]
	    //$scope.pname = oauth2Provider.pd[1]
	    //console.log('d', oauth2Provider.pd)
	    console.log(1234, $scope.img);
	
	    $scope.img = oauth2Provider.pic
	}
	$scope.sh = function () {
	    console.log(123);
	    $scope.showPict();
	}
});

//__________________________________________CreateG______________________________________________________________

conferenceApp.controllers.controller('CreateGroupCtrl', function ($scope, $log, oauth2Provider, $routeParams, HTTP_ERRORS, $location) {
    var history = history || {} 
    history.time_in = new Date()
    history.url = $location.path()
    history.action = history.action || [] 
    history.obj = history.obj || []
    history.val = history.val || []		
    //$scope.parent2=$location.search();
    $scope.conference = $scope.conference || {};
    $scope.template = $scope.template || {};	
    $scope.isValidConference = function (conferenceForm) {
            return !conferenceForm.$invalid //&&
                //$scope.isValidMaxAttendees() &&
                //$scope.isValidDates();
        }	
    
    $scope.loadTemplate = function () {
	  gapi.client.rrrq.load_template().execute(function (resp) {
		$scope.$apply(function () {
		$scope.template = resp
		console.log('1',resp);
		//angular.forEach(resp.group_name, function (conference) {
                //            $scope.template.push(conference);
                //        });
		 });
	  });
    };	
    
    $scope.create = function (conference) {
	  //$scope.conference.tmp = $scope.template.group_url[$scope.conference.tmp]
	  //alert("Your", $scope.conference.old_url )
	  gapi.client.rrrq.copy_template($scope.conference).execute(function (resp) {
		//alert("Your request will be considered", $scope.conference, $scope.conference.old_url);
		console.log('1',$scope.conference);
	  history.action.push("@create_group")
	  for (var k in $scope.conference) {
	      if (history.obj.length < 1) {
	          history.obj.push(k); 
	      }
	      history.val.push($scope.conference[k])	
		console.log('0', k, $scope.conference[k])
	    }
	  $scope.conference = {}
	  console.log('2', history)
	  });
    };	

	$scope.$on("$destroy", function(){
	    history.time_out = new Date()
	    gapi.client.rrrq.timer(history).execute(function (resp) {console.log('dest2', $scope.history)});	
	});

});


/**
 * @ngdoc controller
 * @name DatepickerCtrl
 *
 * @description
 * A controller that holds properties for a datepicker.
 */
conferenceApp.controllers.controller('DatepickerCtrl', function ($scope) {
    $scope.today = function () {
        $scope.dt = new Date();
    };
    $scope.today();

    $scope.clear = function () {
        $scope.dt = null;
    };

    // Disable weekend selection
    $scope.disabled = function (date, mode) {
        return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
    };

    $scope.toggleMin = function () {
        $scope.minDate = ( $scope.minDate ) ? null : new Date();
    };
    $scope.toggleMin();

    $scope.open = function ($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.opened = true;
    };

    $scope.dateOptions = {
        'year-format': "'yy'",
        'starting-day': 1
    };

    $scope.formats = ['dd-MMMM-yyyy', 'yyyy/MM/dd', 'shortDate'];
    $scope.format = $scope.formats[0];
});

conferenceApp.controllers.controller('OAuth2LoginModalCtrl',
    function ($scope, $modalInstance, $rootScope, oauth2Provider) {
        $scope.singInViaModal = function () {
            oauth2Provider.signIn(function () {
                gapi.client.oauth2.userinfo.get().execute(function (resp) {
                    $scope.$root.$apply(function () {
                        oauth2Provider.signedIn = true;
                        $scope.$root.alertStatus = 'success';
                        $scope.$root.rootMessages = 'Logged in with ' + resp.email;
                    });

                    $modalInstance.close();
                });
            });
        };
    });

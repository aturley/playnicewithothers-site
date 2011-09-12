(function (win){
  var userIdCookieName = "pnwoUserId";

  // cookie code from http://www.quirksmode.org/js/cookies.html
  var createCookie = function(name,value,days) {
    if (days) {
      var date = new Date();
      date.setTime(date.getTime()+(days*24*60*60*1000));
      var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
  };

  var readCookie = function(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
      var c = ca[i];
      while (c.charAt(0)==' ') c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
  };

  var eraseCookie = function(name) {
    createCookie(name,"",-1);
  };

  var createUserId = function() {
    // yes, this is a giant hack.
    return ("" + Math.floor(Math.random() * 10000000));
  };

  var storeUserId = function(userId) {
    createCookie(userIdCookieName, userId, 1);
    return userId;
  };

  var getUserId = function() {
    return readCookie(userIdCookieName) || storeUserId(createUserId());
  };

  var User = function() {
    this.userId = getUserId();
  };

  win.User = User;
})(window)

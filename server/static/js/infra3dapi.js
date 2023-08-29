infra3d = { 'version': '3.15.1' };
infra3d.iframe = null;
infra3d.origin = "";
infra3d.cbfpositionchanged = null;
infra3d.scopepositionchanged = null;
infra3d.cbfennloaded = null;
infra3d.scopeennloaded = null;
infra3d.cbfgetlayers = null;
infra3d.scopegetlayers = null;
infra3d.cbfnitialized = null;
infra3d.scopeinitialized = null;
infra3d.cbfpointpicked = null;
infra3d.scopepointpicked = null;
infra3d.cbffeaturepicked = null;
infra3d.scopefeaturepicked = null;
infra3d.cbflrpospicked = null;
infra3d.scopelrpospicked = null;
infra3d.cbfatlrposloaded = null;
infra3d.scopeatlrposloaded = null;
infra3d.cbflayerupdated = null;
infra3d.scopelayerupdated = null;
infra3d.cbflayerchanged = null;
infra3d.scopelayerchanged = null;
infra3d.cbfnetworksloaded = null;
infra3d.scopenetworksloaded = null;
infra3d.cbfcampaignschanged = null;
infra3d.scopecampaignschanged = null;
infra3d.msgevt = function (event) {
   if (event.origin === infra3d.origin) {
      eval(event.data);
   }
};

infra3d.init = function (divid, url, options, cbf, scope) {
   if (options.hasOwnProperty('credentials')) {
      if (options.hasOwnProperty('loginmethod')) {
         if (options["loginmethod"] === "clientside") {
            infra3d.login(url, options["credentials"][0], options["credentials"][1], function (divid) {
               infra3d._init_internal(divid, url, options, cbf, scope);
            }, [divid]);
            return;
         }
      }

      // perform server-side login

      // default auth-url
      var authurl = "https://auth.infra3d.ch/api/v1/login";

      // if set in options override
      if (options.hasOwnProperty("loginurl"))
         authurl = options["loginurl"];

      // append credentials
      authurl += "?username=" + options["credentials"][0] + "&password=" + options["credentials"][1] + "&url=" + url;

      if (!options.hasOwnProperty("origin")) {
         var uri_elements = infra3d._parseURL(url);
         options["origin"] = uri_elements.protocol + "://" + uri_elements.domain;
      }
      url = authurl;
   }

   infra3d._init_internal(divid, url, options, cbf, scope)
};

infra3d._init_internal = function (divid, url, options, cbf, scope) {
   window.removeEventListener('message', infra3d.msgevt);
   window.addEventListener('message', infra3d.msgevt, false);

   var div = document.getElementById(divid);
   var iframe = document.getElementById("infra3dapi");
   if (iframe) {
      iframe.parentNode.removeChild(iframe);
   }

   infra3d.iframe = document.createElement("iFrame");
   infra3d.iframe.id = "infra3dapi";
   infra3d.iframe.style.height = '100%';
   infra3d.iframe.style.width = '100%';
   infra3d.iframe.style.border = 'none';
   infra3d.iframe.style.overflow = 'hidden';
   div.appendChild(infra3d.iframe);

   var urlparams = JSON.parse(JSON.stringify(options));
   var nonurlparams = ["credentials", "loginurl", "origin"];
   for (var nourlparam in nonurlparams) {
      delete urlparams[nonurlparams[nourlparam]];
   }

   var querystring = infra3d._toQueryString(urlparams);
   infra3d.iframe.src = url + "/?" + encodeURIComponent(querystring);
   infra3d.iframe.onload = function () {
      if (cbf !== null && cbf !== undefined) {
         infra3d.cbfinitialized = cbf;
         infra3d.scopeinitialized = scope;
         infra3d.iframe.contentWindow.postMessage("initapi", infra3d.origin);
      }
      infra3d.iframe.contentWindow.focus();
      infra3d.iframe.contentWindow.addEventListener("click", function(evt) {
         infra3d.iframe.contentWindow.focus();
      });
   };

   if (options.hasOwnProperty('origin')) {
      infra3d.origin = options.origin;
   }
   else //Extract the origin from the url
   {
      var uri_elements = infra3d._parseURL(url);
      infra3d.origin = uri_elements.protocol + "://" + uri_elements.domain;
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.oninit = function () {
   infra3d.cbfinitialized.call(infra3d.scopeinitialized);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setMapVisibility = function (isVisible) {
   infra3d.iframe.contentWindow.postMessage("setMapVisibility(" + isVisible + ")", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setLayerVisibility = function (isVisible) {
   infra3d.iframe.contentWindow.postMessage("setLayerVisibility(" + isVisible + ")", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setNavigationVisibility = function (isVisible) {
   infra3d.iframe.contentWindow.postMessage("setNavigationVisibility(" + isVisible + ")", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setButtonVisibility = function (isVisible) {
   infra3d.iframe.contentWindow.postMessage("setButtonVisibility(" + isVisible + ")", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.showLayer = function (layername, isVisible) {
   infra3d.iframe.contentWindow.postMessage("showLayer('" + layername + "'," + isVisible + ")", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.activateLayer = function (layername) {
   infra3d.iframe.contentWindow.postMessage("activateLayer('" + layername + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.loadAtPosition = function (easting, northing, options) {
   infra3d.iframe.contentWindow.postMessage("loadAtPosition(" + easting + "," + northing + ",'" + this._toQueryString(options) + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.lookAtPosition = function (easting, northing, height, options) {
   infra3d.iframe.contentWindow.postMessage("lookAtPosition(" + easting + "," + northing + "," + height + ",'" + this._toQueryString(options) + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.lookAt2DPosition = function (easting, northing, options) {
   infra3d.iframe.contentWindow.postMessage("lookAt2DPosition(" + easting + "," + northing + ",'" + this._toQueryString(options) + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.loadAtEdge = function (edgeid, options) {
   infra3d.iframe.contentWindow.postMessage("loadAtEdge(" + edgeid + ",'" + this._toQueryString(options) + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.loadAtLRPosition = function (axis, sector, km, src, cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("loadAtLRPosition('" + axis + "','" + sector + "'," + km + ",'" + src + "','infra3d.atLRPositionLoaded')", infra3d.origin);
   if (cbf !== null && cbf !== undefined) {
      infra3d.cbfatlrposloaded = cbf;
      infra3d.scopeatlrposloaded = scope;
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.atLRPositionLoaded = function (easting, northing, height, epsg, message) {
   if (infra3d.cbfatlrposloaded !== null) {
      infra3d.cbfatlrposloaded.call(infra3d.scopeatlrposloaded, easting, northing, height, epsg, message);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.getLayers = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("getLayers('infra3d.onLayersLoaded')", infra3d.origin);
   infra3d.cbflayersloaded = cbf;
   infra3d.scopelayersloaded = scope;
};

infra3d.onLayersLoaded = function (layers) {
   if (infra3d.cbflayersloaded !== null) {
      infra3d.cbflayersloaded.call(infra3d.scopelayersloaded, layers);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.highlightFeature = function (id, layername) {
   infra3d.iframe.contentWindow.postMessage("highlightFeature(" + id + ",'" + layername + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.getEnn = function (epsg, cbf, scope, options) {
   infra3d.iframe.contentWindow.postMessage("getEnn(" + epsg + ",'infra3d.onEnnLoaded','" + this._toQueryString(options) + "')", infra3d.origin);
   infra3d.cbfennloaded = cbf;
   infra3d.scopeennloaded = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onEnnLoaded = function (enn) {
   if (infra3d.cbfennloaded !== null) {
      infra3d.cbfennloaded.call(infra3d.scopeennloaded, JSON.parse(enn));
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.getNetworks = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("getNetworks('infra3d.onNetworksLoaded')", infra3d.origin);
   infra3d.cbfnetworksloaded = cbf;
   infra3d.scopenetworksloaded = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onNetworksLoaded = function (networks) {
   if (infra3d.cbfnetworksloaded !== null) {
      infra3d.cbfnetworksloaded.call(infra3d.scopenetworksloaded, JSON.parse(networks));
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.loadAtNetwork = function (network) {
   infra3d.iframe.contentWindow.postMessage("loadAtNetwork('" + network + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onPositionChanged = function (easting, northing, height, epsg, orientation, framenumber, cameraname, cameratype, date, address, campaign) {
   if (infra3d.cbfpositionchanged !== null) {
      infra3d.cbfpositionchanged.call(infra3d.scopepositionchanged, easting, northing, height, epsg, orientation, framenumber, cameraname, cameratype, date, address, campaign);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnPositionChanged = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnPositionChanged('infra3d.onPositionChanged')", infra3d.origin);
   infra3d.cbfpositionchanged = cbf;
   infra3d.scopepositionchanged = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnPositionChanged = function () {
   infra3d.iframe.contentWindow.postMessage("unsetOnPositionChanged()", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onPointPicked = function (
   easting, northing, height, epsg,
   tooltype, imageX, imageY, disparity, quality,
   streamid, framenumber, streamname,
   frameX, frameY, frameZ,
   precFrameX, precFrameY, precFrameZ
) {
   if (infra3d.cbfpointpicked !== null) {
      infra3d.cbfpointpicked.call(
         infra3d.scopepointpicked,
         easting, northing, height, epsg,
         tooltype, imageX, imageY, disparity, quality,
         streamid, framenumber, streamname,
         frameX, frameY, frameZ,
         precFrameX, precFrameY, precFrameZ
      );
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnPointPicked = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnPointPicked('infra3d.onPointPicked')", infra3d.origin);
   infra3d.cbfpointpicked = cbf;
   infra3d.scopepointpicked = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnPointPicked = function () {
   infra3d.iframe.contentWindow.postMessage("unsetOnPointPicked()", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onFeaturePicked = function (feature, layername, selected) {
   if (infra3d.cbffeaturepicked !== null) {
      infra3d.cbffeaturepicked.call(infra3d.scopefeaturepicked, JSON.parse(feature), layername, selected);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnFeaturePicked = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnFeaturePicked('infra3d.onFeaturePicked')", infra3d.origin);
   infra3d.cbffeaturepicked = cbf;
   infra3d.scopefeaturepicked = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnFeaturePicked = function () {
   infra3d.iframe.contentWindow.postMessage("unsetOnFeaturePicked()", infra3d.origin)
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.pickLinearPosition = function (dst, cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("pickLinearPosition('" + dst + "','infra3d.onLinearPositionPicked')", infra3d.origin);
   infra3d.cbflrpospicked = cbf;
   infra3d.scopelrpospicked = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onLinearPositionPicked = function (jsonstring) {
   var lrdata = JSON.parse(jsonstring);
   if (infra3d.cbflrpospicked !== null) {
      infra3d.cbflrpospicked.call(infra3d.scopelrpospicked, lrdata);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnLayerUpdate = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnLayerUpdate('infra3d.onLayerUpdate')", infra3d.origin);
   infra3d.cbflayerupdated = cbf;
   infra3d.scopelayerupdated = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnLayerUpdate = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("unsetOnLayerUpdate()", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onLayerUpdate = function (layername) {
   if (infra3d.cbflayerupdated !== null) {
      infra3d.cbflayerupdated.call(infra3d.scopelayerupdated, layername);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onLayerChanged = function (layername) {
   if (infra3d.cbflayerchanged !== null) {
      infra3d.cbflayerchanged.call(infra3d.scopelayerchanged, layername);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnLayerChanged = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnLayerChanged('infra3d.onLayerChanged')", infra3d.origin);
   infra3d.cbflayerchanged = cbf;
   infra3d.scopelayerchanged = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnLayerChanged = function () {
   infra3d.iframe.contentWindow.postMessage("unsetOnLayerChanged()", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onLogOut = function () {
   if (infra3d.cbflogout !== null) {
      infra3d.cbflogout.call(infra3d.scopelogout);
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnLogOut = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnLogOut('infra3d.onLogOut')", infra3d.origin);
   infra3d.cbflogout = cbf;
   infra3d.scopelogout = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnLogOut = function () {
   infra3d.iframe.contentWindow.postMessage("unsetOnLogOut()", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.setOnCampaignsChanged = function (cbf, scope) {
   infra3d.iframe.contentWindow.postMessage("setOnCampaignsChanged('infra3d.onCampaignsChanged')", infra3d.origin);
   infra3d.cbfcampaignschanged = cbf;
   infra3d.scopecampaignschanged = scope;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.onCampaignsChanged = function (campaigns) {
   if (infra3d.cbfcampaignschanged !== null) {
      infra3d.cbfcampaignschanged.call(infra3d.scopecampaignschanged, JSON.parse(campaigns));
   }
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.unsetOnCampaignsChanged = function () {
   infra3d.iframe.contentWindow.postMessage("unsetOnCampaignsChanged()", infra3d.origin);
   infra3d.cbfcampaignschanged = null;
   infra3d.scopecampaignschanged = null;
};

//---------------------------------------------------------------------------------------------------------------------

infra3d.loadAtCampaign = function (campaign) {
   infra3d.iframe.contentWindow.postMessage("loadAtCampaign('" + campaign + "')", infra3d.origin);
};

//---------------------------------------------------------------------------------------------------------------------

infra3d._parseURL = function (url) {
   var parsed_url = {};

   if (url == null || url.length == 0)
      return parsed_url;

   var protocol_i = url.indexOf('://');
   parsed_url.protocol = url.substr(0, protocol_i);

   var remaining_url = url.substr(protocol_i + 3, url.length);
   var domain_i = remaining_url.indexOf('/');
   domain_i = domain_i == -1 ? remaining_url.length : domain_i;
   parsed_url.domain = remaining_url.substr(0, domain_i);
   parsed_url.path = domain_i == -1 || domain_i + 1 == remaining_url.length ? null : remaining_url.substr(domain_i + 1, remaining_url.length);

   var domain_parts = parsed_url.domain.split('.');
   switch (domain_parts.length) {
      case 2:
         parsed_url.subdomain = null;
         parsed_url.host = domain_parts[0];
         parsed_url.tld = domain_parts[1];
         break;
      case 3:
         parsed_url.subdomain = domain_parts[0];
         parsed_url.host = domain_parts[1];
         parsed_url.tld = domain_parts[2];
         break;
      case 4:
         parsed_url.subdomain = domain_parts[0];
         parsed_url.host = domain_parts[1];
         parsed_url.tld = domain_parts[2] + '.' + domain_parts[3];
         break;
   }

   parsed_url.parent_domain = parsed_url.host + '.' + parsed_url.tld;

   return parsed_url;
};

infra3d._toQueryString = function (object) {
   if (object) {
      var querystring = "";
      for (var i = 0; i < Object.keys(object).length; i++) {
         querystring += Object.keys(object)[i] + "=" + object[Object.keys(object)[i]] + "&";
      }
      return querystring.slice(0, -1);
   }
   else {
      return "";
   }
};

infra3d.login = function (url, username, password, callback, cbargs) {
   var cbargs = cbargs || [];
   if (url[url.length - 1] != "/")
      url += "/";
   var initialRequest = new XMLHttpRequest();
   initialRequest.withCredentials = true;
   //The initial Request will get redirected two or more times before we land at the login page.
   initialRequest.open("GET", url, true);
   initialRequest.onreadystatechange = function () {
      if (initialRequest.readyState === 4 && initialRequest.status === 200) {
         //If this first response's URL is the same as the originaly requested one,
         //it means that we are already logged in or the resource was not protected.
         var start = initialRequest.responseText.search("/idp/profile");
         var end = initialRequest.responseText.search("method") - 2;
         var actionURL = "";
         if (url.search("devel") > 0)
            actionURL = "https://idp.devel.infra3d.ch";
         else
            actionURL = "https://idp.infra3d.ch";
         actionURL += initialRequest.responseText.slice(start, end);

         if (start < 0) {
            console.log("Already logged in");
            callback.apply(this, cbargs);
         }

         //The redirection led us to the login form of our IDP. The responseURL is
         // where the username and password must get POSTed.
         var params = "j_username=" + username + "&j_password=" + password + "&_eventId_proceed=";

         var secondRequest = new XMLHttpRequest();
         secondRequest.withCredentials = true;
         secondRequest.open("POST", actionURL);
         secondRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
         secondRequest.onreadystatechange = function () {
            if (secondRequest.readyState == 4 && secondRequest.status == 200) {
               //We get the SAML assertion packed in an HTML document, so we need to parse it and get the assertion.
               var doc = new DOMParser().parseFromString(secondRequest.responseText, 'text/html');
               var theForm = doc.getElementsByTagName("form");
               if (theForm.length > 0) {
                  var theURL = theForm[0].action;
                  var params = theForm[0][0].name + "=" + encodeURIComponent(theForm[0][0].value) + "&" + theForm[0][1].name + "=" + encodeURIComponent(theForm[0][1].value);

                  var thirdRequest = new XMLHttpRequest();
                  //We know the URL of the IDP to login from the parsed response.
                  thirdRequest.withCredentials = true;
                  thirdRequest.open("POST", theURL);
                  thirdRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                  thirdRequest.onreadystatechange = function () {
                     if (thirdRequest.readyState == 4 && thirdRequest.status == 200) {
                        console.log("Login successful");
                        callback.apply(this, cbargs);
                     }
                  };
                  thirdRequest.send(params);
               }
               else {
                  return null;
               }
            }
         };
         secondRequest.send(params);
      }
   };
   initialRequest.send();
};

//==ClosureCompiler==
//@compilation_levelADVANCED_OPTIMIZATIONS
//@externs_urlhttps://raw.githubusercontent.com/google/closure-compiler/master/contrib/externs/maps/google_maps_api_v3.js
//==/ClosureCompiler==

/**
 *@nameMarkerClustererforGoogleMapsv3
 *@versionversion1.0
 *@authorLukeMahe
 *@fileoverview
 *Thelibrarycreatesandmanagesper-zoom-levelclustersforlargeamountsof
 *markers.
 *<br/>
 *Thisisav3implementationofthe
 *<ahref="http://gmaps-utility-library-dev.googlecode.com/svn/tags/markerclusterer/"
 *>v2MarkerClusterer</a>.
 */

/**
 *@license
 *Copyright2010GoogleInc.AllRightsReserved.
 *
 *LicensedundertheApacheLicense,Version2.0(the"License");
 *youmaynotusethisfileexceptincompliancewiththeLicense.
 *YoumayobtainacopyoftheLicenseat
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 *Unlessrequiredbyapplicablelaworagreedtoinwriting,software
 *distributedundertheLicenseisdistributedonan"ASIS"BASIS,
 *WITHOUTWARRANTIESORCONDITIONSOFANYKIND,eitherexpressorimplied.
 *SeetheLicenseforthespecificlanguagegoverningpermissionsand
 *limitationsundertheLicense.
 */


/**
 *AMarkerClustererthatclustersmarkers.
 *
 *@param{google.maps.Map}mapTheGooglemaptoattachto.
 *@param{Array.<google.maps.Marker>=}opt_markersOptionalmarkerstoaddto
 *  thecluster.
 *@param{Object=}opt_optionssupportthefollowingoptions:
 *    'gridSize':(number)Thegridsizeofaclusterinpixels.
 *    'maxZoom':(number)Themaximumzoomlevelthatamarkercanbepartofa
 *               cluster.
 *    'zoomOnClick':(boolean)Whetherthedefaultbehaviourofclickingona
 *                   clusteristozoomintoit.
 *    'averageCenter':(boolean)Whetherthecenterofeachclustershouldbe
 *                     theaverageofallmarkersinthecluster.
 *    'minimumClusterSize':(number)Theminimumnumberofmarkerstobeina
 *                          clusterbeforethemarkersarehiddenandacount
 *                          isshown.
 *    'styles':(object)Anobjectthathasstyleproperties:
 *      'url':(string)Theimageurl.
 *      'height':(number)Theimageheight.
 *      'width':(number)Theimagewidth.
 *      'anchor':(Array)Theanchorpositionofthelabeltext.
 *      'textColor':(string)Thetextcolor.
 *      'textSize':(number)Thetextsize.
 *      'backgroundPosition':(string)Thepositionofthebackgoundx,y.
 *      'iconAnchor':(Array)Theanchorpositionoftheiconx,y.
 *@constructor
 *@extendsgoogle.maps.OverlayView
 */
functionMarkerClusterer(map,opt_markers,opt_options){
  //MarkerClustererimplementsgoogle.maps.OverlayViewinterface.Weusethe
  //extendfunctiontoextendMarkerClustererwithgoogle.maps.OverlayView
  //becauseitmightnotalwaysbeavailablewhenthecodeisdefinedsowe
  //lookforitatthelastpossiblemoment.Ifitdoesn'texistnowthen
  //thereisnopointgoingahead:)
  this.extend(MarkerClusterer,google.maps.OverlayView);
  this.map_=map;

  /**
   *@type{Array.<google.maps.Marker>}
   *@private
   */
  this.markers_=[];

  /**
   * @type{Array.<Cluster>}
   */
  this.clusters_=[];

  this.sizes=[53,56,66,78,90];

  /**
   *@private
   */
  this.styles_=[];

  /**
   *@type{boolean}
   *@private
   */
  this.ready_=false;

  varoptions=opt_options||{};

  /**
   *@type{number}
   *@private
   */
  this.gridSize_=options['gridSize']||60;

  /**
   *@private
   */
  this.minClusterSize_=options['minimumClusterSize']||2;


  /**
   *@type{?number}
   *@private
   */
  this.maxZoom_=options['maxZoom']||null;

  this.styles_=options['styles']||[];

  /**
   *@type{string}
   *@private
   */
  this.imagePath_=options['imagePath']||
      this.MARKER_CLUSTER_IMAGE_PATH_;

  /**
   *@type{string}
   *@private
   */
  this.imageExtension_=options['imageExtension']||
      this.MARKER_CLUSTER_IMAGE_EXTENSION_;

  /**
   *@type{boolean}
   *@private
   */
  this.zoomOnClick_=true;

  if(options['zoomOnClick']!=undefined){
    this.zoomOnClick_=options['zoomOnClick'];
  }

  /**
   *@type{boolean}
   *@private
   */
  this.averageCenter_=false;

  if(options['averageCenter']!=undefined){
    this.averageCenter_=options['averageCenter'];
  }

  this.setupStyles_();

  this.setMap(map);

  /**
   *@type{number}
   *@private
   */
  this.prevZoom_=this.map_.getZoom();

  //Addthemapeventlisteners
  varthat=this;
  google.maps.event.addListener(this.map_,'zoom_changed',function(){
    varzoom=that.map_.getZoom();

    if(that.prevZoom_!=zoom){
      that.prevZoom_=zoom;
      that.resetViewport();
    }
  });

  google.maps.event.addListener(this.map_,'idle',function(){
    that.redraw();
  });

  //Finally,addthemarkers
  if(opt_markers&&opt_markers.length){
    this.addMarkers(opt_markers,false);
  }
}


/**
 *Themarkerclusterimagepath.
 *
 *@type{string}
 *@private
 */
MarkerClusterer.prototype.MARKER_CLUSTER_IMAGE_PATH_='../images/m';


/**
 *Themarkerclusterimagepath.
 *
 *@type{string}
 *@private
 */
MarkerClusterer.prototype.MARKER_CLUSTER_IMAGE_EXTENSION_='png';


/**
 *Extendsaobjectsprototypebyanothers.
 *
 *@param{Object}obj1Theobjecttobeextended.
 *@param{Object}obj2Theobjecttoextendwith.
 *@return{Object}Thenewextendedobject.
 *@ignore
 */
MarkerClusterer.prototype.extend=function(obj1,obj2){
  return(function(object){
    for(varpropertyinobject.prototype){
      this.prototype[property]=object.prototype[property];
    }
    returnthis;
  }).apply(obj1,[obj2]);
};


/**
 *Implementaionoftheinterfacemethod.
 *@ignore
 */
MarkerClusterer.prototype.onAdd=function(){
  this.setReady_(true);
};

/**
 *Implementaionoftheinterfacemethod.
 *@ignore
 */
MarkerClusterer.prototype.draw=function(){};

/**
 *Setsupthestylesobject.
 *
 *@private
 */
MarkerClusterer.prototype.setupStyles_=function(){
  if(this.styles_.length){
    return;
  }

  for(vari=0,size;size=this.sizes[i];i++){
    this.styles_.push({
      url:this.imagePath_+(i+1)+'.'+this.imageExtension_,
      height:size,
      width:size
    });
  }
};

/**
 * Fitthemaptotheboundsofthemarkersintheclusterer.
 */
MarkerClusterer.prototype.fitMapToMarkers=function(){
  varmarkers=this.getMarkers();
  varbounds=newgoogle.maps.LatLngBounds();
  for(vari=0,marker;marker=markers[i];i++){
    bounds.extend(marker.getPosition());
  }

  this.map_.fitBounds(bounds);
};


/**
 * Setsthestyles.
 *
 * @param{Object}stylesThestyletoset.
 */
MarkerClusterer.prototype.setStyles=function(styles){
  this.styles_=styles;
};


/**
 * Getsthestyles.
 *
 * @return{Object}Thestylesobject.
 */
MarkerClusterer.prototype.getStyles=function(){
  returnthis.styles_;
};


/**
 *Whetherzoomonclickisset.
 *
 *@return{boolean}TrueifzoomOnClick_isset.
 */
MarkerClusterer.prototype.isZoomOnClick=function(){
  returnthis.zoomOnClick_;
};

/**
 *Whetheraveragecenterisset.
 *
 *@return{boolean}TrueifaverageCenter_isset.
 */
MarkerClusterer.prototype.isAverageCenter=function(){
  returnthis.averageCenter_;
};


/**
 * Returnsthearrayofmarkersintheclusterer.
 *
 * @return{Array.<google.maps.Marker>}Themarkers.
 */
MarkerClusterer.prototype.getMarkers=function(){
  returnthis.markers_;
};


/**
 * Returnsthenumberofmarkersintheclusterer
 *
 * @return{Number}Thenumberofmarkers.
 */
MarkerClusterer.prototype.getTotalMarkers=function(){
  returnthis.markers_.length;
};


/**
 * Setsthemaxzoomfortheclusterer.
 *
 * @param{number}maxZoomThemaxzoomlevel.
 */
MarkerClusterer.prototype.setMaxZoom=function(maxZoom){
  this.maxZoom_=maxZoom;
};


/**
 * Getsthemaxzoomfortheclusterer.
 *
 * @return{number}Themaxzoomlevel.
 */
MarkerClusterer.prototype.getMaxZoom=function(){
  returnthis.maxZoom_;
};


/**
 * Thefunctionforcalculatingtheclustericonimage.
 *
 * @param{Array.<google.maps.Marker>}markersThemarkersintheclusterer.
 * @param{number}numStylesThenumberofstylesavailable.
 * @return{Object}Aobjectproperties:'text'(string)and'index'(number).
 * @private
 */
MarkerClusterer.prototype.calculator_=function(markers,numStyles){
  varindex=0;
  varcount=markers.length;
  vardv=count;
  while(dv!==0){
    dv=parseInt(dv/10,10);
    index++;
  }

  index=Math.min(index,numStyles);
  return{
    text:count,
    index:index
  };
};


/**
 *Setthecalculatorfunction.
 *
 *@param{function(Array,number)}calculatorThefunctiontosetasthe
 *    calculator.Thefunctionshouldreturnaobjectproperties:
 *    'text'(string)and'index'(number).
 *
 */
MarkerClusterer.prototype.setCalculator=function(calculator){
  this.calculator_=calculator;
};


/**
 *Getthecalculatorfunction.
 *
 *@return{function(Array,number)}thecalculatorfunction.
 */
MarkerClusterer.prototype.getCalculator=function(){
  returnthis.calculator_;
};


/**
 *Addanarrayofmarkerstotheclusterer.
 *
 *@param{Array.<google.maps.Marker>}markersThemarkerstoadd.
 *@param{boolean=}opt_nodrawWhethertoredrawtheclusters.
 */
MarkerClusterer.prototype.addMarkers=function(markers,opt_nodraw){
  for(vari=0,marker;marker=markers[i];i++){
    this.pushMarkerTo_(marker);
  }
  if(!opt_nodraw){
    this.redraw();
  }
};


/**
 *Pushesamarkertotheclusterer.
 *
 *@param{google.maps.Marker}markerThemarkertoadd.
 *@private
 */
MarkerClusterer.prototype.pushMarkerTo_=function(marker){
  marker.isAdded=false;
  if(marker['draggable']){
    //Ifthemarkerisdraggableaddalistenersoweupdatetheclusterson
    //thedragend.
    varthat=this;
    google.maps.event.addListener(marker,'dragend',function(){
      marker.isAdded=false;
      that.repaint();
    });
  }
  this.markers_.push(marker);
};


/**
 *Addsamarkertotheclustererandredrawsifneeded.
 *
 *@param{google.maps.Marker}markerThemarkertoadd.
 *@param{boolean=}opt_nodrawWhethertoredrawtheclusters.
 */
MarkerClusterer.prototype.addMarker=function(marker,opt_nodraw){
  this.pushMarkerTo_(marker);
  if(!opt_nodraw){
    this.redraw();
  }
};


/**
 *Removesamarkerandreturnstrueifremoved,falseifnot
 *
 *@param{google.maps.Marker}markerThemarkertoremove
 *@return{boolean}Whetherthemarkerwasremovedornot
 *@private
 */
MarkerClusterer.prototype.removeMarker_=function(marker){
  varindex=-1;
  if(this.markers_.indexOf){
    index=this.markers_.indexOf(marker);
  }else{
    for(vari=0,m;m=this.markers_[i];i++){
      if(m==marker){
        index=i;
        break;
      }
    }
  }

  if(index==-1){
    //Markerisnotinourlistofmarkers.
    returnfalse;
  }

  marker.setMap(null);

  this.markers_.splice(index,1);

  returntrue;
};


/**
 *Removeamarkerfromthecluster.
 *
 *@param{google.maps.Marker}markerThemarkertoremove.
 *@param{boolean=}opt_nodrawOptionalbooleantoforcenoredraw.
 *@return{boolean}Trueifthemarkerwasremoved.
 */
MarkerClusterer.prototype.removeMarker=function(marker,opt_nodraw){
  varremoved=this.removeMarker_(marker);

  if(!opt_nodraw&&removed){
    this.resetViewport();
    this.redraw();
    returntrue;
  }else{
   returnfalse;
  }
};


/**
 *Removesanarrayofmarkersfromthecluster.
 *
 *@param{Array.<google.maps.Marker>}markersThemarkerstoremove.
 *@param{boolean=}opt_nodrawOptionalbooleantoforcenoredraw.
 */
MarkerClusterer.prototype.removeMarkers=function(markers,opt_nodraw){
  varremoved=false;

  for(vari=0,marker;marker=markers[i];i++){
    varr=this.removeMarker_(marker);
    removed=removed||r;
  }

  if(!opt_nodraw&&removed){
    this.resetViewport();
    this.redraw();
    returntrue;
  }
};


/**
 *Setstheclusterer'sreadystate.
 *
 *@param{boolean}readyThestate.
 *@private
 */
MarkerClusterer.prototype.setReady_=function(ready){
  if(!this.ready_){
    this.ready_=ready;
    this.createClusters_();
  }
};


/**
 *Returnsthenumberofclustersintheclusterer.
 *
 *@return{number}Thenumberofclusters.
 */
MarkerClusterer.prototype.getTotalClusters=function(){
  returnthis.clusters_.length;
};


/**
 *Returnsthegooglemapthattheclustererisassociatedwith.
 *
 *@return{google.maps.Map}Themap.
 */
MarkerClusterer.prototype.getMap=function(){
  returnthis.map_;
};


/**
 *Setsthegooglemapthattheclustererisassociatedwith.
 *
 *@param{google.maps.Map}mapThemap.
 */
MarkerClusterer.prototype.setMap=function(map){
  this.map_=map;
};


/**
 *Returnsthesizeofthegrid.
 *
 *@return{number}Thegridsize.
 */
MarkerClusterer.prototype.getGridSize=function(){
  returnthis.gridSize_;
};


/**
 *Setsthesizeofthegrid.
 *
 *@param{number}sizeThegridsize.
 */
MarkerClusterer.prototype.setGridSize=function(size){
  this.gridSize_=size;
};


/**
 *Returnstheminclustersize.
 *
 *@return{number}Thegridsize.
 */
MarkerClusterer.prototype.getMinClusterSize=function(){
  returnthis.minClusterSize_;
};

/**
 *Setstheminclustersize.
 *
 *@param{number}sizeThegridsize.
 */
MarkerClusterer.prototype.setMinClusterSize=function(size){
  this.minClusterSize_=size;
};


/**
 *Extendsaboundsobjectbythegridsize.
 *
 *@param{google.maps.LatLngBounds}boundsTheboundstoextend.
 *@return{google.maps.LatLngBounds}Theextendedbounds.
 */
MarkerClusterer.prototype.getExtendedBounds=function(bounds){
  varprojection=this.getProjection();

  //Turntheboundsintolatlng.
  vartr=newgoogle.maps.LatLng(bounds.getNorthEast().lat(),
      bounds.getNorthEast().lng());
  varbl=newgoogle.maps.LatLng(bounds.getSouthWest().lat(),
      bounds.getSouthWest().lng());

  //Convertthepointstopixelsandtheextendoutbythegridsize.
  vartrPix=projection.fromLatLngToDivPixel(tr);
  trPix.x+=this.gridSize_;
  trPix.y-=this.gridSize_;

  varblPix=projection.fromLatLngToDivPixel(bl);
  blPix.x-=this.gridSize_;
  blPix.y+=this.gridSize_;

  //ConvertthepixelpointsbacktoLatLng
  varne=projection.fromDivPixelToLatLng(trPix);
  varsw=projection.fromDivPixelToLatLng(blPix);

  //Extendtheboundstocontainthenewbounds.
  bounds.extend(ne);
  bounds.extend(sw);

  returnbounds;
};


/**
 *Determinsifamarkeriscontainedinabounds.
 *
 *@param{google.maps.Marker}markerThemarkertocheck.
 *@param{google.maps.LatLngBounds}boundsTheboundstocheckagainst.
 *@return{boolean}Trueifthemarkerisinthebounds.
 *@private
 */
MarkerClusterer.prototype.isMarkerInBounds_=function(marker,bounds){
  returnbounds.contains(marker.getPosition());
};


/**
 *Clearsallclustersandmarkersfromtheclusterer.
 */
MarkerClusterer.prototype.clearMarkers=function(){
  this.resetViewport(true);

  //Setthemarkersaemptyarray.
  this.markers_=[];
};


/**
 *Clearsallexistingclustersandrecreatesthem.
 *@param{boolean}opt_hideToalsohidethemarker.
 */
MarkerClusterer.prototype.resetViewport=function(opt_hide){
  //Removealltheclusters
  for(vari=0,cluster;cluster=this.clusters_[i];i++){
    cluster.remove();
  }

  //Resetthemarkerstonotbeaddedandtobeinvisible.
  for(vari=0,marker;marker=this.markers_[i];i++){
    marker.isAdded=false;
    if(opt_hide){
      marker.setMap(null);
    }
  }

  this.clusters_=[];
};

/**
 *
 */
MarkerClusterer.prototype.repaint=function(){
  varoldClusters=this.clusters_.slice();
  this.clusters_.length=0;
  this.resetViewport();
  this.redraw();

  //Removetheoldclusters.
  //Doitinatimeoutsotheotherclustershavebeendrawnfirst.
  window.setTimeout(function(){
    for(vari=0,cluster;cluster=oldClusters[i];i++){
      cluster.remove();
    }
  },0);
};


/**
 *Redrawstheclusters.
 */
MarkerClusterer.prototype.redraw=function(){
  this.createClusters_();
};


/**
 *Calculatesthedistancebetweentwolatlnglocationsinkm.
 *@seehttp://www.movable-type.co.uk/scripts/latlong.html
 *
 *@param{google.maps.LatLng}p1Thefirstlatlngpoint.
 *@param{google.maps.LatLng}p2Thesecondlatlngpoint.
 *@return{number}Thedistancebetweenthetwopointsinkm.
 *@private
*/
MarkerClusterer.prototype.distanceBetweenPoints_=function(p1,p2){
  if(!p1||!p2){
    return0;
  }

  varR=6371;//RadiusoftheEarthinkm
  vardLat=(p2.lat()-p1.lat())*Math.PI/180;
  vardLon=(p2.lng()-p1.lng())*Math.PI/180;
  vara=Math.sin(dLat/2)*Math.sin(dLat/2)+
    Math.cos(p1.lat()*Math.PI/180)*Math.cos(p2.lat()*Math.PI/180)*
    Math.sin(dLon/2)*Math.sin(dLon/2);
  varc=2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  vard=R*c;
  returnd;
};


/**
 *Addamarkertoacluster,orcreatesanewcluster.
 *
 *@param{google.maps.Marker}markerThemarkertoadd.
 *@private
 */
MarkerClusterer.prototype.addToClosestCluster_=function(marker){
  vardistance=40000;//Somelargenumber
  varclusterToAddTo=null;
  varpos=marker.getPosition();
  for(vari=0,cluster;cluster=this.clusters_[i];i++){
    varcenter=cluster.getCenter();
    if(center){
      vard=this.distanceBetweenPoints_(center,marker.getPosition());
      if(d<distance){
        distance=d;
        clusterToAddTo=cluster;
      }
    }
  }

  if(clusterToAddTo&&clusterToAddTo.isMarkerInClusterBounds(marker)){
    clusterToAddTo.addMarker(marker);
  }else{
    varcluster=newCluster(this);
    cluster.addMarker(marker);
    this.clusters_.push(cluster);
  }
};


/**
 *Createstheclusters.
 *
 *@private
 */
MarkerClusterer.prototype.createClusters_=function(){
  if(!this.ready_){
    return;
  }

  //Getourcurrentmapviewbounds.
  //Createanewboundsobjectsowedon'taffectthemap.
  varmapBounds=newgoogle.maps.LatLngBounds(this.map_.getBounds().getSouthWest(),
      this.map_.getBounds().getNorthEast());
  varbounds=this.getExtendedBounds(mapBounds);

  for(vari=0,marker;marker=this.markers_[i];i++){
    if(!marker.isAdded&&this.isMarkerInBounds_(marker,bounds)){
      this.addToClosestCluster_(marker);
    }
  }
};


/**
 *Aclusterthatcontainsmarkers.
 *
 *@param{MarkerClusterer}markerClustererThemarkerclustererthatthis
 *    clusterisassociatedwith.
 *@constructor
 *@ignore
 */
functionCluster(markerClusterer){
  this.markerClusterer_=markerClusterer;
  this.map_=markerClusterer.getMap();
  this.gridSize_=markerClusterer.getGridSize();
  this.minClusterSize_=markerClusterer.getMinClusterSize();
  this.averageCenter_=markerClusterer.isAverageCenter();
  this.center_=null;
  this.markers_=[];
  this.bounds_=null;
  this.clusterIcon_=newClusterIcon(this,markerClusterer.getStyles(),
      markerClusterer.getGridSize());
}

/**
 *Determinsifamarkerisalreadyaddedtothecluster.
 *
 *@param{google.maps.Marker}markerThemarkertocheck.
 *@return{boolean}Trueifthemarkerisalreadyadded.
 */
Cluster.prototype.isMarkerAlreadyAdded=function(marker){
  if(this.markers_.indexOf){
    returnthis.markers_.indexOf(marker)!=-1;
  }else{
    for(vari=0,m;m=this.markers_[i];i++){
      if(m==marker){
        returntrue;
      }
    }
  }
  returnfalse;
};


/**
 *Addamarkerthecluster.
 *
 *@param{google.maps.Marker}markerThemarkertoadd.
 *@return{boolean}Trueifthemarkerwasadded.
 */
Cluster.prototype.addMarker=function(marker){
  if(this.isMarkerAlreadyAdded(marker)){
    returnfalse;
  }

  if(!this.center_){
    this.center_=marker.getPosition();
    this.calculateBounds_();
  }else{
    if(this.averageCenter_){
      varl=this.markers_.length+1;
      varlat=(this.center_.lat()*(l-1)+marker.getPosition().lat())/l;
      varlng=(this.center_.lng()*(l-1)+marker.getPosition().lng())/l;
      this.center_=newgoogle.maps.LatLng(lat,lng);
      this.calculateBounds_();
    }
  }

  marker.isAdded=true;
  this.markers_.push(marker);

  varlen=this.markers_.length;
  if(len<this.minClusterSize_&&marker.getMap()!=this.map_){
    //Minclustersizenotreachedsoshowthemarker.
    marker.setMap(this.map_);
  }

  if(len==this.minClusterSize_){
    //Hidethemarkersthatwereshowing.
    for(vari=0;i<len;i++){
      this.markers_[i].setMap(null);
    }
  }

  if(len>=this.minClusterSize_){
    marker.setMap(null);
  }

  this.updateIcon();
  returntrue;
};


/**
 *Returnsthemarkerclustererthattheclusterisassociatedwith.
 *
 *@return{MarkerClusterer}Theassociatedmarkerclusterer.
 */
Cluster.prototype.getMarkerClusterer=function(){
  returnthis.markerClusterer_;
};


/**
 *Returnstheboundsofthecluster.
 *
 *@return{google.maps.LatLngBounds}theclusterbounds.
 */
Cluster.prototype.getBounds=function(){
  varbounds=newgoogle.maps.LatLngBounds(this.center_,this.center_);
  varmarkers=this.getMarkers();
  for(vari=0,marker;marker=markers[i];i++){
    bounds.extend(marker.getPosition());
  }
  returnbounds;
};


/**
 *Removesthecluster
 */
Cluster.prototype.remove=function(){
  this.clusterIcon_.remove();
  this.markers_.length=0;
  deletethis.markers_;
};


/**
 *Returnsthecenterofthecluster.
 *
 *@return{number}Theclustercenter.
 */
Cluster.prototype.getSize=function(){
  returnthis.markers_.length;
};


/**
 *Returnsthecenterofthecluster.
 *
 *@return{Array.<google.maps.Marker>}Theclustercenter.
 */
Cluster.prototype.getMarkers=function(){
  returnthis.markers_;
};


/**
 *Returnsthecenterofthecluster.
 *
 *@return{google.maps.LatLng}Theclustercenter.
 */
Cluster.prototype.getCenter=function(){
  returnthis.center_;
};


/**
 *Calculatedtheextendedboundsoftheclusterwiththegrid.
 *
 *@private
 */
Cluster.prototype.calculateBounds_=function(){
  varbounds=newgoogle.maps.LatLngBounds(this.center_,this.center_);
  this.bounds_=this.markerClusterer_.getExtendedBounds(bounds);
};


/**
 *Determinesifamarkerliesintheclustersbounds.
 *
 *@param{google.maps.Marker}markerThemarkertocheck.
 *@return{boolean}Trueifthemarkerliesinthebounds.
 */
Cluster.prototype.isMarkerInClusterBounds=function(marker){
  returnthis.bounds_.contains(marker.getPosition());
};


/**
 *Returnsthemapthattheclusterisassociatedwith.
 *
 *@return{google.maps.Map}Themap.
 */
Cluster.prototype.getMap=function(){
  returnthis.map_;
};


/**
 *Updatestheclustericon
 */
Cluster.prototype.updateIcon=function(){
  varzoom=this.map_.getZoom();
  varmz=this.markerClusterer_.getMaxZoom();

  if(mz&&zoom>mz){
    //Thezoomisgreaterthanourmaxzoomsoshowallthemarkersincluster.
    for(vari=0,marker;marker=this.markers_[i];i++){
      marker.setMap(this.map_);
    }
    return;
  }

  if(this.markers_.length<this.minClusterSize_){
    //Minclustersizenotyetreached.
    this.clusterIcon_.hide();
    return;
  }

  varnumStyles=this.markerClusterer_.getStyles().length;
  varsums=this.markerClusterer_.getCalculator()(this.markers_,numStyles);
  this.clusterIcon_.setCenter(this.center_);
  this.clusterIcon_.setSums(sums);
  this.clusterIcon_.show();
};


/**
 *Aclustericon
 *
 *@param{Cluster}clusterTheclustertobeassociatedwith.
 *@param{Object}stylesAnobjectthathasstyleproperties:
 *    'url':(string)Theimageurl.
 *    'height':(number)Theimageheight.
 *    'width':(number)Theimagewidth.
 *    'anchor':(Array)Theanchorpositionofthelabeltext.
 *    'textColor':(string)Thetextcolor.
 *    'textSize':(number)Thetextsize.
 *    'backgroundPosition:(string)Thebackgroundpostitionx,y.
 *@param{number=}opt_paddingOptionalpaddingtoapplytotheclustericon.
 *@constructor
 *@extendsgoogle.maps.OverlayView
 *@ignore
 */
functionClusterIcon(cluster,styles,opt_padding){
  cluster.getMarkerClusterer().extend(ClusterIcon,google.maps.OverlayView);

  this.styles_=styles;
  this.padding_=opt_padding||0;
  this.cluster_=cluster;
  this.center_=null;
  this.map_=cluster.getMap();
  this.div_=null;
  this.sums_=null;
  this.visible_=false;

  this.setMap(this.map_);
}


/**
 *Triggerstheclusterclickeventandzoom'siftheoptionisset.
 *
 *@param{google.maps.MouseEvent}eventTheeventtopropagate
 */
ClusterIcon.prototype.triggerClusterClick=function(event){
  varmarkerClusterer=this.cluster_.getMarkerClusterer();

  //Triggertheclusterclickevent.
  google.maps.event.trigger(markerClusterer,'clusterclick',this.cluster_,event);

  if(markerClusterer.isZoomOnClick()){
    //Zoomintothecluster.
    this.map_.fitBounds(this.cluster_.getBounds());
  }
};


/**
 *Addingtheclustericontothedom.
 *@ignore
 */
ClusterIcon.prototype.onAdd=function(){
  this.div_=document.createElement('DIV');
  if(this.visible_){
    varpos=this.getPosFromLatLng_(this.center_);
    this.div_.style.cssText=this.createCss(pos);
    this.div_.innerHTML=this.sums_.text;
  }

  varpanes=this.getPanes();
  panes.overlayMouseTarget.appendChild(this.div_);

  varthat=this;
  varisDragging=false;
  google.maps.event.addDomListener(this.div_,'click',function(event){
    //Onlyperformclickwhennotprecededbyadrag
    if(!isDragging){
      that.triggerClusterClick(event);
    }
  });
  google.maps.event.addDomListener(this.div_,'mousedown',function(){
    isDragging=false;
  });
  google.maps.event.addDomListener(this.div_,'mousemove',function(){
    isDragging=true;
  });
};


/**
 *Returnsthepositiontoplacethedivdendingonthelatlng.
 *
 *@param{google.maps.LatLng}latlngThepositioninlatlng.
 *@return{google.maps.Point}Thepositioninpixels.
 *@private
 */
ClusterIcon.prototype.getPosFromLatLng_=function(latlng){
  varpos=this.getProjection().fromLatLngToDivPixel(latlng);

  if(typeofthis.iconAnchor_==='object'&&this.iconAnchor_.length===2){
    pos.x-=this.iconAnchor_[0];
    pos.y-=this.iconAnchor_[1];
  }else{
    pos.x-=parseInt(this.width_/2,10);
    pos.y-=parseInt(this.height_/2,10);
  }
  returnpos;
};


/**
 *Drawtheicon.
 *@ignore
 */
ClusterIcon.prototype.draw=function(){
  if(this.visible_){
    varpos=this.getPosFromLatLng_(this.center_);
    this.div_.style.top=pos.y+'px';
    this.div_.style.left=pos.x+'px';
  }
};


/**
 *Hidetheicon.
 */
ClusterIcon.prototype.hide=function(){
  if(this.div_){
    this.div_.style.display='none';
  }
  this.visible_=false;
};


/**
 *Positionandshowtheicon.
 */
ClusterIcon.prototype.show=function(){
  if(this.div_){
    varpos=this.getPosFromLatLng_(this.center_);
    this.div_.style.cssText=this.createCss(pos);
    this.div_.style.display='';
  }
  this.visible_=true;
};


/**
 *Removetheiconfromthemap
 */
ClusterIcon.prototype.remove=function(){
  this.setMap(null);
};


/**
 *ImplementationoftheonRemoveinterface.
 *@ignore
 */
ClusterIcon.prototype.onRemove=function(){
  if(this.div_&&this.div_.parentNode){
    this.hide();
    this.div_.parentNode.removeChild(this.div_);
    this.div_=null;
  }
};


/**
 *Setthesumsoftheicon.
 *
 *@param{Object}sumsThesumscontaining:
 *  'text':(string)Thetexttodisplayintheicon.
 *  'index':(number)Thestyleindexoftheicon.
 */
ClusterIcon.prototype.setSums=function(sums){
  this.sums_=sums;
  this.text_=sums.text;
  this.index_=sums.index;
  if(this.div_){
    this.div_.innerHTML=sums.text;
  }

  this.useStyle();
};


/**
 *Setstheicontothethestyles.
 */
ClusterIcon.prototype.useStyle=function(){
  varindex=Math.max(0,this.sums_.index-1);
  index=Math.min(this.styles_.length-1,index);
  varstyle=this.styles_[index];
  this.url_=style['url'];
  this.height_=style['height'];
  this.width_=style['width'];
  this.textColor_=style['textColor'];
  this.anchor_=style['anchor'];
  this.textSize_=style['textSize'];
  this.backgroundPosition_=style['backgroundPosition'];
  this.iconAnchor_=style['iconAnchor'];
};


/**
 *Setsthecenteroftheicon.
 *
 *@param{google.maps.LatLng}centerThelatlngtosetasthecenter.
 */
ClusterIcon.prototype.setCenter=function(center){
  this.center_=center;
};


/**
 *Createthecsstextbasedonthepositionoftheicon.
 *
 *@param{google.maps.Point}posTheposition.
 *@return{string}Thecssstyletext.
 */
ClusterIcon.prototype.createCss=function(pos){
  varstyle=[];
  style.push('background-image:url('+this.url_+');');
  varbackgroundPosition=this.backgroundPosition_?this.backgroundPosition_:'00';
  style.push('background-position:'+backgroundPosition+';');

  if(typeofthis.anchor_==='object'){
    if(typeofthis.anchor_[0]==='number'&&this.anchor_[0]>0&&
        this.anchor_[0]<this.height_){
      style.push('height:'+(this.height_-this.anchor_[0])+
          'px;padding-top:'+this.anchor_[0]+'px;');
    }elseif(typeofthis.anchor_[0]==='number'&&this.anchor_[0]<0&&
        -this.anchor_[0]<this.height_){
      style.push('height:'+this.height_+'px;line-height:'+(this.height_+this.anchor_[0])+
          'px;');
    }else{
      style.push('height:'+this.height_+'px;line-height:'+this.height_+
          'px;');
    }
    if(typeofthis.anchor_[1]==='number'&&this.anchor_[1]>0&&
        this.anchor_[1]<this.width_){
      style.push('width:'+(this.width_-this.anchor_[1])+
          'px;padding-left:'+this.anchor_[1]+'px;');
    }else{
      style.push('width:'+this.width_+'px;text-align:center;');
    }
  }else{
    style.push('height:'+this.height_+'px;line-height:'+
        this.height_+'px;width:'+this.width_+'px;text-align:center;');
  }

  vartxtColor=this.textColor_?this.textColor_:'black';
  vartxtSize=this.textSize_?this.textSize_:11;

  style.push('cursor:pointer;top:'+pos.y+'px;left:'+
      pos.x+'px;color:'+txtColor+';position:absolute;font-size:'+
      txtSize+'px;font-family:Arial,sans-serif;font-weight:bold');
  returnstyle.join('');
};


//ExportSymbolsforClosure
//Ifyouarenotgoingtocompilewithclosurethenyoucanremovethe
//codebelow.
window['MarkerClusterer']=MarkerClusterer;
MarkerClusterer.prototype['addMarker']=MarkerClusterer.prototype.addMarker;
MarkerClusterer.prototype['addMarkers']=MarkerClusterer.prototype.addMarkers;
MarkerClusterer.prototype['clearMarkers']=
    MarkerClusterer.prototype.clearMarkers;
MarkerClusterer.prototype['fitMapToMarkers']=
    MarkerClusterer.prototype.fitMapToMarkers;
MarkerClusterer.prototype['getCalculator']=
    MarkerClusterer.prototype.getCalculator;
MarkerClusterer.prototype['getGridSize']=
    MarkerClusterer.prototype.getGridSize;
MarkerClusterer.prototype['getExtendedBounds']=
    MarkerClusterer.prototype.getExtendedBounds;
MarkerClusterer.prototype['getMap']=MarkerClusterer.prototype.getMap;
MarkerClusterer.prototype['getMarkers']=MarkerClusterer.prototype.getMarkers;
MarkerClusterer.prototype['getMaxZoom']=MarkerClusterer.prototype.getMaxZoom;
MarkerClusterer.prototype['getStyles']=MarkerClusterer.prototype.getStyles;
MarkerClusterer.prototype['getTotalClusters']=
    MarkerClusterer.prototype.getTotalClusters;
MarkerClusterer.prototype['getTotalMarkers']=
    MarkerClusterer.prototype.getTotalMarkers;
MarkerClusterer.prototype['redraw']=MarkerClusterer.prototype.redraw;
MarkerClusterer.prototype['removeMarker']=
    MarkerClusterer.prototype.removeMarker;
MarkerClusterer.prototype['removeMarkers']=
    MarkerClusterer.prototype.removeMarkers;
MarkerClusterer.prototype['resetViewport']=
    MarkerClusterer.prototype.resetViewport;
MarkerClusterer.prototype['repaint']=
    MarkerClusterer.prototype.repaint;
MarkerClusterer.prototype['setCalculator']=
    MarkerClusterer.prototype.setCalculator;
MarkerClusterer.prototype['setGridSize']=
    MarkerClusterer.prototype.setGridSize;
MarkerClusterer.prototype['setMaxZoom']=
    MarkerClusterer.prototype.setMaxZoom;
MarkerClusterer.prototype['onAdd']=MarkerClusterer.prototype.onAdd;
MarkerClusterer.prototype['draw']=MarkerClusterer.prototype.draw;

Cluster.prototype['getCenter']=Cluster.prototype.getCenter;
Cluster.prototype['getSize']=Cluster.prototype.getSize;
Cluster.prototype['getMarkers']=Cluster.prototype.getMarkers;

ClusterIcon.prototype['onAdd']=ClusterIcon.prototype.onAdd;
ClusterIcon.prototype['draw']=ClusterIcon.prototype.draw;
ClusterIcon.prototype['onRemove']=ClusterIcon.prototype.onRemove;

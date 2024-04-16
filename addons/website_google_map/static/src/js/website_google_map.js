functioninitialize_map(){
    'usestrict';

    //MAPCONFIGANDLOADING
    varmap=newgoogle.maps.Map(document.getElementById('flectra-google-map'),{
        zoom:1,
        center:{lat:0.0,lng:0.0},
        mapTypeId:google.maps.MapTypeId.ROADMAP
    });

    //ENABLEADDRESSGEOCODING
    varGeocoder=newgoogle.maps.Geocoder();

    //INFOBUBBLES
    varinfoWindow=newgoogle.maps.InfoWindow();
    varpartners=newgoogle.maps.MarkerImage('/website_google_map/static/src/img/partners.png',newgoogle.maps.Size(25,25));
    varpartner_url=document.body.getAttribute('data-partner-url')||'';
    varmarkers=[];
    varoptions={
        imagePath:'/website_google_map/static/src/lib/images/m'
    };

    google.maps.event.addListener(map,'click',function(){
        infoWindow.close();
    });

    //Displaythebubbleonceclicked
    varonMarkerClick=function(){
        varmarker=this;
        varp=marker.partner;
        infoWindow.setContent(
              '<divclass="marker">'+
              (partner_url.length?'<atarget="_top"href="'+partner_url+p.id+'"><b>'+p.name+'</b></a>':'<b>'+p.name+'</b>')+
              (p.type?' <b>'+p.type+'</b>':'')+
              ' <pre>'+p.address+'</pre>'+
              '</div>'
          );
        infoWindow.open(map,marker);
    };

    //Createabubbleforapartner
    varset_marker=function(partner){
        //Ifnolat&long,geocodeaddress
        //TODO:aservercronjobthatwillstorethesecoordinatesindatabaseinsteadofresolvingthemon-the-fly
        if(!partner.latitude&&!partner.longitude){
            Geocoder.geocode({'address':partner.address},function(results,status){
                if(status===google.maps.GeocoderStatus.OK){
                    varlocation=results[0].geometry.location;
                    partner.latitude=location.ob;
                    partner.longitude=location.pb;
                    varmarker=newgoogle.maps.Marker({
                        partner:partner,
                        map:map,
                        icon:partners,
                        position:location
                    });
                    google.maps.event.addListener(marker,'click',onMarkerClick);
                    markers.push(marker);
                }else{
                    console.debug('Geocodewasnotsuccessfulforthefollowingreason:'+status);
                }
            });
        }else{
            varlatLng=newgoogle.maps.LatLng(partner.latitude,partner.longitude);
            varmarker=newgoogle.maps.Marker({
                partner:partner,
                icon:partners,
                map:map,
                position:latLng
            });
            google.maps.event.addListener(marker,'click',onMarkerClick);
            markers.push(marker);
        }
    };

    //Createthemarkersandclusterthemonthemap
    if(flectra_partner_data){/*flectra_partner_dataspecialvariableshouldhavebeendefinedingoogle_map.xml*/
        for(vari=0;i<flectra_partner_data.counter;i++){
            set_marker(flectra_partner_data.partners[i]);
        }
        varmarkerCluster=newMarkerClusterer(map,markers,options);
    }
}

//InitializemaponcetheDOMhasbeenloaded
google.maps.event.addDomListener(window,'load',initialize_map);

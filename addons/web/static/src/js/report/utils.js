flectra.define('report.utils',function(require){
'usestrict';

functionget_protocol_from_url(url){
    vara=document.createElement('a');
    a.href=url;
    returna.protocol;
}

functionget_host_from_url(url){
    vara=document.createElement('a');
    a.href=url;
    returna.host;
}

functionbuild_origin(protocol,host){
    returnprotocol+'//'+host;
}

return{
    'get_protocol_from_url':get_protocol_from_url,
    'get_host_from_url':get_host_from_url,
    'build_origin':build_origin,
};

});
